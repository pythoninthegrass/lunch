#!/usr/bin/env python

import random
from datetime import datetime
from decouple import config
from fasthtml.common import *
from pathlib import Path
from pony.orm import *


PORT = config('PORT', default=8080, cast=int)
RELOAD = config('RELOAD', default=True, cast=bool)

css = Path("static/styles.css").read_text()
# javascript = Path("static/script.js").read_text()

hdrs = (
    Link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"),
    HighlightJS(langs=['python', 'javascript', 'html', 'css']),
    # Script(javascript),
    # Style(css),
)

app, rt = fast_app(
    static_path='static',
    hdrs=hdrs,
    pico=True,
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
    """Create database and tables if they don't exist."""
    if not db_fn.exists():
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
        # Get recent restaurants
        recent = select(r.restaurant for r in RecentLunch).order_by(desc(RecentLunch.date))[:14]
        recent = set(recent)

        # Filter out recent ones
        available = [r for r in restaurants if r not in recent]
        if not available:
            available = restaurants

        choice = random.choice(available)

        # Add to recent and cleanup old entries
        RecentLunch(restaurant=choice)

        # Keep only latest 14 entries
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


@rt('/')
def index():
    return Titled(
        "Lunch",
        Container(
            H2("Click below to find out what's for Lunch", style="text-align: center; margin-bottom: 2rem;"),
            Div(
                Div(
                    Input(type="radio", name="option", value="cheap", id="cheap", checked=True),
                    Label("Cheap", for_="cheap", style="margin-right: 1rem;"),
                    Input(type="radio", name="option", value="normal", id="normal"),
                    Label("Normal", for_="normal"),
                    style="margin-bottom: 2rem;",
                ),
                style="text-align: center;",
            ),
            Div(
                Button(
                    "Roll Lunch",
                    hx_post="/roll",
                    hx_include="[name='option']",
                    hx_target="#result",
                    style="margin: 0 0.5rem 1rem;",
                ),
                Button("Add Restaurant", hx_get="/add-form", hx_target="#form-area", style="margin: 0 0.5rem 1rem;"),
                Button("Delete Restaurant", hx_get="/delete-form", hx_target="#form-area", style="margin: 0 0.5rem 1rem;"),
                Button("List All", hx_get="/list", hx_target="#result", style="margin-bottom: 1rem;"),
                style="text-align: center;",
            ),
            Div(id="result", style="margin-top: 1rem; text-align: center;"),
            Div(id="form-area", style="margin-top: 1rem; text-align: center;"),
            style="max-width: 800px; margin: 0 auto; padding: 2rem;",
        ),
    )


@rt('/roll')
def roll(option: str):
    restaurant = rng_restaurant(option)
    if restaurant:
        return P(f"Today's {option} lunch is at: {restaurant}", cls="text-xl")
    return P("No restaurants found for that option!", cls="text-red-500")


@rt('/list')
@db_session
def list():
    restaurants = select((r.restaurant, r.option) for r in LunchList) \
        .order_by(lambda r1, r2: r1[0] > r2[0])[:]
    if not restaurants:
        return P("No restaurants found!", cls="text-red-500")

    return (
        Div(
            H2("All Restaurants"),
            Table(
                Tr(Th("Restaurant"), Th("Type")),
                *[Tr(Td(name), Td(option.title())) for name, option in restaurants],
                cls="table"
            )
        )
    )


@rt('/add-form')
def add_form():
    return Form(
        H3("Add Restaurant"),
        Input(name="name", placeholder="Restaurant name", required=True),
        Input(type="radio", name="option", value="cheap", id="add-cheap", checked=True),
        Label("Cheap", for_="add-cheap"),
        Input(type="radio", name="option", value="normal", id="add-normal"),
        Label("Normal", for_="add-normal"),
        Button("Add", type="submit"),
        hx_post="/add",
        hx_target="#result",
    )


@rt('/add')
def add(name: str, option: str):
    result = add_restaurant(name, option)
    if result is False:
        return P(f"{name} already exists!", cls="text-red-500")
    return P(f"Added {name}!", cls="text-green-500")


@rt('/delete-form')
def delete_form():
    restaurants = get_all_restaurants()
    if not restaurants:
        return P("No restaurants to delete!", cls="text-red-500")

    return Form(
        H3("Delete Restaurant"),
        Select(name="name", required=True)(*[Option(r, value=r) for r in restaurants]),
        Button("Delete", type="submit"),
        hx_post="/delete",
        hx_target="#result",
    )


@rt('/delete')
def post(name: str):
    result = delete_restaurant(name)
    if result is None:
        return P("Restaurant not found!", cls="text-red-500")
    return P(f"{name} deleted!", cls="text-green-500")


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
