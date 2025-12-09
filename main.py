#!/usr/bin/env python

import random
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

from decouple import config
from fasthtml.common import *
from pony.orm import *

PORT = config('PORT', default=8080, cast=int)
RELOAD = config('RELOAD', default=True, cast=bool)

# Local assets only - no CDN (works offline)
hdrs = (
    Link(rel="stylesheet", href="basecoat.min.css"),
    Link(rel="stylesheet", href="app.css"),
    Link(rel="stylesheet", href="fonts/fontawesome.min.css"),
    Script(src="js/basecoat/basecoat.min.js", defer=True),
)

static_dir = Path(__file__).parent / "static"

app, rt = fast_app(
    static_path=str(static_dir),
    hdrs=hdrs,
    pico=False,
    secret_key='lunch-app-secret',
)

db = Database()


class LunchList(db.Entity):
    id = PrimaryKey(int, auto=True)
    restaurant = Required(str, unique=True)
    option = Required(str)


class RecentLunch(db.Entity):
    id = PrimaryKey(int, auto=True)
    restaurant = Required(str)
    date = Required(datetime, default=datetime.now)


db_fn = Path(__file__).parent / "lunch.db"
lunch_list_fn = Path(__file__).parent / "lunch_list.csv"
recent_lunch_fn = Path(__file__).parent / "recent_lunch.csv"

db.bind(provider='sqlite', filename=str(db_fn), create_db=True)
db.generate_mapping(create_tables=True)


@db_session
def create_db_and_tables():
    """Seed database from CSV if tables are empty."""
    if LunchList.select().count() == 0:
        with open(lunch_list_fn, "r") as f:
            for line in f:
                if line.startswith("restaurant"):
                    continue
                restaurant, option = line.strip().split(",")
                LunchList(restaurant=restaurant, option=option)

        with open(recent_lunch_fn, "r") as f:
            for line in f:
                if line.startswith("restaurant"):
                    continue
                restaurant, date = line.strip().split(",")
                date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
                RecentLunch(restaurant=restaurant, date=date)


@db_session
def get_all_restaurants():
    """Return list of all restaurants."""
    return select(r.restaurant for r in LunchList)[:]


@db_session
def get_all_restaurants_with_option():
    """Return list of (name, option) tuples, sorted by name."""
    return select((r.restaurant, r.option) for r in LunchList).order_by(1)[:]


@db_session
def get_restaurants(option):
    """Return list of restaurants based on cost."""
    return select(r.restaurant for r in LunchList if r.option.lower() == option.lower())[:]


@db_session
def rng_restaurant(option):
    """Return random restaurant based on cost."""
    restaurants = get_restaurants(option)
    if not restaurants:
        return None

    if option.lower() != 'cheap' and len(restaurants) >= 15:
        recent = select(r.restaurant for r in RecentLunch).order_by(desc(RecentLunch.date))[:14]
        recent = set(recent)

        available = [r for r in restaurants if r not in recent]
        if not available:
            available = restaurants

        choice = random.choice(available)

        RecentLunch(restaurant=choice)

        old_entries = select(r for r in RecentLunch).order_by(desc(RecentLunch.date))[14:]
        for entry in old_entries:
            entry.delete()

        return choice

    return random.choice(restaurants)


@db_session
def add_restaurant(name, option):
    """Add restaurant to database."""
    if LunchList.exists(lambda r: r.restaurant.lower() == name.lower()):
        return False

    LunchList(restaurant=name, option=option)
    return True


@db_session
def delete_restaurant(name):
    """Delete restaurant from database."""
    restaurant = LunchList.get(lambda r: r.restaurant.lower() == name.lower())
    if not restaurant:
        return None

    restaurant.delete()
    return True


# Layout Components

def theme_toggle_script():
    """Theme toggle + system detection"""
    return Script("""
    (() => {
        const stored = localStorage.getItem('themeMode');
        const useSystem = localStorage.getItem('useSystemTheme') !== 'false';
        const prefersDark = matchMedia('(prefers-color-scheme: dark)').matches;

        if (useSystem) {
            if (prefersDark) document.documentElement.classList.add('dark');
        } else if (stored === 'dark') {
            document.documentElement.classList.add('dark');
        }

        matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
            if (localStorage.getItem('useSystemTheme') !== 'false') {
                document.documentElement.classList.toggle('dark', e.matches);
            }
        });

        window.toggleTheme = () => {
            const isDark = !document.documentElement.classList.contains('dark');
            document.documentElement.classList.toggle('dark', isDark);
            localStorage.setItem('themeMode', isDark ? 'dark' : 'light');
            localStorage.setItem('useSystemTheme', 'false');
        };

        window.setSystemTheme = (useSystem) => {
            localStorage.setItem('useSystemTheme', useSystem);
            if (useSystem) {
                const prefersDark = matchMedia('(prefers-color-scheme: dark)').matches;
                document.documentElement.classList.toggle('dark', prefersDark);
            }
        };
    })();
    """)


def theme_toggle_btn():
    """Theme toggle icon (top-right)"""
    return Div(
        I(cls="fas fa-sun sun-icon"),
        I(cls="fas fa-moon moon-icon"),
        cls="theme-toggle",
        onclick="toggleTheme()",
        style="cursor: pointer; font-size: 1.25rem;",
    )


def bottom_nav(active):
    """4-tab bottom navigation"""
    tabs = [
        ("home", "fa-home", "Home", "/"),
        ("add", "fa-plus", "Add", "/add"),
        ("list", "fa-list", "List", "/list"),
        ("settings", "fa-cog", "Settings", "/settings"),
    ]
    return Nav(
        *[nav_item(id, icon, label, href, active) for id, icon, label, href in tabs],
        cls="bottom-nav"
    )


def nav_item(id, icon, label, href, active):
    return A(
        I(cls=f"fas {icon}"),
        Span(label),
        href=href,
        cls=f"nav-item {'active' if id == active else ''}",
    )


def Layout(*content, active_tab="home"):
    """Main app layout with nav bar"""
    # Theme toggle only shown on home page (matches Flet app behavior)
    show_theme_toggle = active_tab == "home"
    return Html(
        Head(
            Title("Lunch"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            *hdrs,
        ),
        Body(
            theme_toggle_script(),
            theme_toggle_btn() if show_theme_toggle else "",
            Div(*content, cls="main-content", id="main-content"),
            bottom_nav(active_tab),
            cls="app-container",
        ),
    )


# View Components

def home_view(result=None):
    return Div(
        Img(src="logo.png", cls="banner-img mb-6"),
        Div(
            Label(
                Input(type="radio", name="option", value="cheap", id="cheap"),
                " Cheap",
                cls="radio-label",
            ),
            Label(
                Input(type="radio", name="option", value="normal", id="normal", checked=True),
                " Normal",
                cls="radio-label",
            ),
            cls="radio-group mb-6",
        ),
        Button(
            "Roll Lunch",
            hx_post="/roll",
            hx_include="[name='option']",
            hx_target="#result",
            cls="btn",
            style="display: block; margin: 0 auto;",
        ),
        Div(result or "", id="result", cls="text-center text-xl font-semibold mt-6"),
        cls="text-center",
    )


def add_view(message=None):
    return Div(
        H1("Add Restaurant", cls="text-2xl font-bold text-center mb-6"),
        Form(
            Div(
                Input(
                    name="name",
                    placeholder="Restaurant Name",
                    required=True,
                    cls="form-input",
                ),
                cls="mb-4",
            ),
            Div(
                Div(
                    Label(
                        Input(type="radio", name="option", value="cheap", id="add-cheap"),
                        " Cheap",
                        cls="radio-label",
                    ),
                    Label(
                        Input(type="radio", name="option", value="normal", id="add-normal", checked=True),
                        " Normal",
                        cls="radio-label",
                    ),
                    cls="radio-group",
                ),
                cls="mb-4",
            ),
            Button("Add Restaurant", type="submit", cls="btn w-full"),
            hx_post="/add",
            hx_target="#add-result",
            hx_swap="innerHTML",
            cls="max-w-sm mx-auto",
        ),
        Div(message or "", id="add-result", cls="text-center mt-4"),
    )


def list_view():
    restaurants = get_all_restaurants_with_option()
    return Div(
        H1("All Restaurants", cls="text-2xl font-bold text-center mb-6"),
        Div(
            *[restaurant_card(name, option) for name, option in restaurants],
            cls="card",
        ) if restaurants else P("No restaurants found", cls="text-center text-muted"),
        id="restaurant-list",
    )


def restaurant_card(name, option):
    price = "$" if option.lower() == "cheap" else "$$"
    return Div(
        Span(name, cls="flex-1"),
        Span(price, cls="px-2 font-semibold price-indicator", title=option.title()),
        Button(
            I(cls="fas fa-trash"),
            cls="delete-btn",
            hx_post=f"/delete?name={quote(name)}",
            hx_target="#restaurant-list",
            hx_confirm=f"Delete {name}?",
        ),
        cls="restaurant-card",
    )


def settings_view():
    return Div(
        H1("Settings", cls="text-2xl font-bold text-center mb-6"),
        Div(
            Div(
                Div(
                    I(cls="fas fa-font", style="font-size: 1.25rem;"),
                    Label(
                        Input(
                            type="checkbox",
                            role="switch",
                            id="system-theme",
                            checked=True,
                            onchange="setSystemTheme(this.checked)",
                        ),
                        " Match system theme",
                        cls="flex items-center gap-3",
                    ),
                    cls="flex items-center gap-3",
                ),
                P(
                    "When enabled, follows your device's appearance setting. "
                    "When disabled, use the icon in the top-right to toggle manually.",
                    cls="text-sm text-muted mt-2",
                ),
                cls="p-4",
            ),
            cls="card mb-4",
        ),
        Div(
            Div(
                H3("About", cls="font-semibold"),
                P("Lunch - Restaurant Selector"),
                P("Version 1.0.0", cls="text-sm text-muted"),
                cls="p-4",
            ),
            cls="card",
        ),
    )


# Routes

@rt('/')
def get():
    return Layout(home_view(), active_tab="home")


@rt('/add')
def get_add():
    return Layout(add_view(), active_tab="add")


@rt('/list')
def get_list():
    return Layout(list_view(), active_tab="list")


@rt('/settings')
def get_settings():
    return Layout(settings_view(), active_tab="settings")


@rt('/roll')
def post_roll(option: str):
    restaurant = rng_restaurant(option)
    if restaurant:
        return Span(restaurant, cls="text-xl font-semibold")
    return Span("No restaurants found!", cls="text-destructive")


@rt('/add')
def post_add(name: str, option: str):
    result = add_restaurant(name, option)
    if result:
        return Span(f"Added restaurant: {name} ({option.title()})", cls="text-success")
    return Span(f"Restaurant '{name}' already exists!", cls="text-destructive")


@rt('/delete')
def post_delete(name: str):
    delete_restaurant(name)
    return list_view()


if __name__ == '__main__':
    create_db_and_tables()
    serve(
        host='0.0.0.0',
        port=PORT,
        reload=RELOAD,
        reload_includes=[
            'static/*.css',
            'static/*.js',
        ],
        reload_excludes=['scratch.py'],
    )
