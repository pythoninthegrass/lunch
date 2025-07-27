"""
Restaurant service module containing all business logic for restaurant management.
This module is decoupled from the frontend and handles all restaurant operations.
"""

from typing import List, Optional, Set, Tuple


class RestaurantService:
    """Service class for restaurant management business logic."""

    def __init__(self, db_manager):
        """Initialize with a database manager dependency."""
        self.db = db_manager
        self.session_rolled_restaurants = {"cheap": set(), "Normal": set()}

    def initialize(self) -> None:
        """Initialize the restaurant service and database."""
        self.db.create_db_and_tables()

    def get_all_restaurants(self) -> list[tuple[str, str]]:
        """Get all restaurants from the database."""
        return self.db.get_all_restaurants()

    def get_restaurants_by_category(self, category: str) -> list[tuple[str, str]]:
        """Get restaurants filtered by category (cheap/Normal)."""
        return self.db.get_restaurants(category)

    def add_restaurant(self, name: str, category: str) -> str:
        """
        Add a new restaurant to the database.
        Returns success message or raises exception.
        """
        try:
            self.db.add_restaurant_to_db(name, category)
            return f"Added restaurant: {name} ({category})"
        except ValueError as e:
            raise e
        except Exception as e:
            raise Exception(f"Error adding restaurant: {str(e)}")

    def delete_restaurant(self, name: str) -> str:
        """
        Delete a restaurant from the database.
        Returns success message or raises exception.
        """
        try:
            self.db.delete_restaurant_from_db(name)
            return f"Deleted restaurant: {name}"
        except ValueError as e:
            raise e
        except Exception as e:
            raise Exception(f"Error deleting restaurant: {str(e)}")

    def select_restaurant(self, category: str = "Normal") -> tuple[str, str]:
        """
        Select a restaurant for lunch using round-robin logic.
        Returns the selected restaurant or raises exception.
        """
        try:
            restaurant = self.db.calculate_lunch(category, self.session_rolled_restaurants[category])
            return restaurant
        except ValueError as e:
            if "No restaurants found" in str(e):
                raise ValueError(f"No {category.lower()} restaurants available. Add some restaurants first!")
            else:
                raise e
        except Exception as e:
            raise Exception(f"Error selecting restaurant: {str(e)}")

    def get_random_restaurant(self, category: str) -> tuple[str, str]:
        """Get a random restaurant with the specified category."""
        try:
            return self.db.rng_restaurant(category)
        except ValueError as e:
            raise e
        except Exception as e:
            raise Exception(f"Error getting random restaurant: {str(e)}")

    def reset_session_for_category(self, category: str) -> None:
        """Reset the session rolled restaurants for a specific category."""
        if category in self.session_rolled_restaurants:
            self.session_rolled_restaurants[category].clear()

    def reset_all_sessions(self) -> None:
        """Reset all session rolled restaurants."""
        for category in self.session_rolled_restaurants:
            self.session_rolled_restaurants[category].clear()
