#!/usr/bin/env python

"""FastHTML web application for restaurant selection."""

import contextlib
import os
import sys
from pathlib import Path


def get_base_path() -> Path:
    """Get the base path for the application.

    When running as a PyInstaller bundle, returns the path to the
    temporary directory where files are extracted (sys._MEIPASS).
    Otherwise returns the project root directory.
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    return Path(__file__).parent.parent


def is_frozen() -> bool:
    """Check if running as a PyInstaller bundle or PEX executable."""
    return getattr(sys, 'frozen', False) or os.environ.get('PEX') is not None


# Add project root to path for direct execution (not needed when frozen)
if not is_frozen():
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

from app.backend.db import (
    add_restaurant_to_db,
    calculate_lunch,
    create_db_and_tables,
    delete_restaurant_from_db,
    get_all_restaurants,
)
from decouple import config
from fasthtml.common import *
from urllib.parse import quote

PORT = config('PORT', default=8080, cast=int)
RELOAD = config('RELOAD', default=True, cast=bool) and not is_frozen()

# Theme state for Tauri polling
current_theme = "light"

# Local assets only - no CDN (works offline)
hdrs = (
    Link(rel="stylesheet", href="basecoat.min.css"),
    Link(rel="stylesheet", href="app.css"),
    Link(rel="stylesheet", href="fonts/fontawesome.min.css"),
    Script(src="js/htmx.min.js"),
    Script(src="js/basecoat/basecoat.min.js", defer=True),
)

# Static directory: use _MEIPASS when frozen, otherwise relative to source
static_dir = get_base_path() / "app" / "static"

application, rt = fast_app(
    static_path=str(static_dir),
    hdrs=hdrs,
    pico=False,
    secret_key='lunch-app-secret',
)


# Layout Components

def theme_toggle_script():
    """Theme toggle + system detection"""
    return Script("""
    (() => {
        const stored = localStorage.getItem('themeMode');
        const useSystem = localStorage.getItem('useSystemTheme') !== 'false';
        const prefersDark = matchMedia('(prefers-color-scheme: dark)').matches;

        // Sync theme to server (for Tauri window theme polling)
        const syncThemeToServer = (isDark) => {
            const theme = isDark ? 'dark' : 'light';
            fetch('/api/theme', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'theme=' + theme
            }).catch(() => {});
        };

        let initialDark = false;
        if (useSystem) {
            initialDark = prefersDark;
        } else if (stored === 'dark') {
            initialDark = true;
        }
        if (initialDark) {
            document.documentElement.classList.add('dark');
        }
        syncThemeToServer(initialDark);

        matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
            if (localStorage.getItem('useSystemTheme') !== 'false') {
                document.documentElement.classList.toggle('dark', e.matches);
                syncThemeToServer(e.matches);
            }
        });

        window.toggleTheme = () => {
            const isDark = !document.documentElement.classList.contains('dark');
            document.documentElement.classList.toggle('dark', isDark);
            localStorage.setItem('themeMode', isDark ? 'dark' : 'light');
            localStorage.setItem('useSystemTheme', 'false');
            syncThemeToServer(isDark);
        };

        window.setSystemTheme = (useSystem) => {
            localStorage.setItem('useSystemTheme', useSystem);
            if (useSystem) {
                const prefersDark = matchMedia('(prefers-color-scheme: dark)').matches;
                document.documentElement.classList.toggle('dark', prefersDark);
                syncThemeToServer(prefersDark);
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
    return Html(
        Head(
            Title("Lunch"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            *hdrs,
        ),
        Body(
            theme_toggle_script(),
            Div(*content, cls="main-content", id="main-content"),
            bottom_nav(active_tab),
            cls="app-container",
        ),
    )


# View Components

def home_view(result=None):
    return Div(
        Div(
            theme_toggle_btn(),
            Img(src="logo.png", cls="banner-img"),
            cls="logo-container",
        ),
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
            cls="radio-group",
        ),
        Button(
            "Roll Lunch",
            hx_post="/roll",
            hx_include="[name='option']",
            hx_target="#result",
            cls="btn",
            style="display: block; margin: 0 auto;",
        ),
        Div(result or "", id="result", cls="text-center text-xl font-semibold"),
        cls="text-center home-content",
    )


def add_view(message=None):
    return Div(
        H1("Add Restaurant", cls="text-2xl font-bold text-center"),
        Form(
            Input(
                name="name",
                placeholder="",
                required=True,
                autofocus=True,
                cls="form-input",
            ),
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
            Button("Add Restaurant", type="submit", cls="btn w-full"),
            hx_post="/add",
            hx_target="#add-result",
            hx_swap="innerHTML",
            cls="add-form",
            **{"hx-on::after-request": "this.reset()"},
        ),
        Div(message or "", id="add-result", cls="text-center"),
        cls="add-content",
    )


def list_view():
    restaurants = get_all_restaurants()
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
            type="button",
            cls="delete-btn",
            hx_post=f"/delete?name={quote(name)}",
            hx_target="#restaurant-list",
            hx_swap="outerHTML",
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


@rt('/add', methods=['GET'])
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
    try:
        restaurant = calculate_lunch(option)
        if restaurant:
            # calculate_lunch returns (name, option) tuple
            return Span(restaurant[0], cls="text-xl font-semibold")
    except ValueError:
        pass
    return Span("No restaurants found!", cls="text-destructive")


@rt('/add', methods=['POST'])
def post_add(name: str, option: str):
    try:
        add_restaurant_to_db(name, option)
        return Span(
            f"Added restaurant: {name} ({option.title()})",
            id="add-success-msg",
            cls="text-success",
            **{"hx-on::load": "setTimeout(() => this.remove(), 5000)"},
        )
    except ValueError:
        return Span(f"Restaurant '{name}' already exists!", cls="text-destructive")

@rt('/delete')
def post_delete(name: str):
    with contextlib.suppress(ValueError):
        delete_restaurant_from_db(name)
    return list_view()


@rt('/shutdown', methods=['POST'])
def post_shutdown():
    """Shutdown endpoint for Tauri sidecar lifecycle management.

    Only responds to localhost requests. Exits the process cleanly.
    """
    os._exit(0)


@rt('/api/theme', methods=['GET'])
def get_theme():
    """Return current theme for Tauri window sync."""
    return current_theme


@rt('/api/theme', methods=['POST'])
def set_theme(theme: str):
    """Set current theme (called by frontend JS)."""
    global current_theme
    if theme in ('light', 'dark'):
        current_theme = theme
    return current_theme


create_db_and_tables()

# * serve() is only called when this module runs as __main__ (direct execution)
# * When uvicorn imports app.main:application for reload, it skips this
if __name__ == '__main__':
    if is_frozen():
        # When frozen, run uvicorn directly with the app object (no reload possible)
        import uvicorn
        uvicorn.run(application, host='0.0.0.0', port=PORT)
    else:
        # Development: use serve() with reload support
        serve(appname='app.main', app='application', port=PORT, reload=RELOAD)
