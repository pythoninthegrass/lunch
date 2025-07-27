#!/usr/bin/env python

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


def create_app(page: ft.Page):
    """Create and initialize the lunch application."""
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
        return restaurant_service.add_restaurant(name, category)

    def delete_restaurant_callback(name: str) -> str:
        return restaurant_service.delete_restaurant(name)

    def get_all_restaurants_callback():
        return restaurant_service.get_all_restaurants()

    # Set callbacks in GUI
    gui.set_callbacks(roll_lunch_callback, add_restaurant_callback, delete_restaurant_callback, get_all_restaurants_callback)


if __name__ == "__main__":
    ft.run(create_app)
