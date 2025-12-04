#!/usr/bin/env python

import sys
from pathlib import Path

# Add project root to path for consistent imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.logging import setup_logging

# Initialize logging before other imports
setup_logging()

import flet as ft
from backend.db import (
    add_restaurant_to_db,
    calculate_lunch,
    create_db_and_tables,
    delete_restaurant_from_db,
    get_all_restaurants,
    rng_restaurant,
)
from backend.service import RestaurantService
from frontend.gui import create_gui


class DatabaseManager:
    """Database manager wrapper for dependency injection."""

    def create_db_and_tables(self):
        return create_db_and_tables()

    def get_all_restaurants(self):
        return get_all_restaurants()

    def get_restaurants(self, option):
        from backend.db import get_restaurants

        return get_restaurants(option)

    def add_restaurant_to_db(self, name, option):
        return add_restaurant_to_db(name, option)

    def delete_restaurant_from_db(self, name):
        return delete_restaurant_from_db(name)

    def calculate_lunch(self, option, session_rolled):
        return calculate_lunch(option, session_rolled)

    def rng_restaurant(self, option):
        return rng_restaurant(option)


async def create_app(page: ft.Page):
    """Create and initialize the lunch application (async for proper event loop integration)."""
    # Initialize backend service
    db_manager = DatabaseManager()
    restaurant_service = RestaurantService(db_manager)
    restaurant_service.initialize()

    # Create frontend GUI
    gui = create_gui(page)

    # Define callback functions for GUI
    def roll_lunch_callback(category: str) -> str:
        restaurant = restaurant_service.select_restaurant(category)
        return restaurant[0]

    def add_restaurant_callback(name: str, category: str) -> str:
        result = restaurant_service.add_restaurant(name, category)
        # Schedule sync lookup in separate thread via Flet's thread scheduler
        page.run_thread(restaurant_service.lookup_info_sync, name)
        return result

    def delete_restaurant_callback(name: str) -> str:
        return restaurant_service.delete_restaurant(name)

    def get_all_restaurants_callback():
        return restaurant_service.get_all_restaurants()

    # Set callbacks in GUI
    gui.set_callbacks(roll_lunch_callback, add_restaurant_callback, delete_restaurant_callback, get_all_restaurants_callback)


if __name__ == "__main__":
    assets_dir = Path(__file__).parent / "static"
    ft.app(create_app, assets_dir=str(assets_dir))
