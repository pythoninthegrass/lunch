"""
Restaurant service module containing all business logic for restaurant management.
This module is decoupled from the frontend and handles all restaurant operations.
"""

import threading
from app.backend.db import save_restaurant_info
from app.backend.logging import setup_logging, start_action

setup_logging()


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
        with start_action(action_type="list_restaurants") as action:
            restaurants = self.db.get_all_restaurants()
            action.add_success_fields(count=len(restaurants))
            return restaurants

    def get_restaurants_by_category(self, category: str) -> list[tuple[str, str]]:
        """Get restaurants filtered by category (cheap/Normal)."""
        return self.db.get_restaurants(category)

    def add_restaurant(self, name: str, category: str) -> str:
        """
        Add a new restaurant to the database.
        Returns success message or raises exception.

        Note: Info lookup should be triggered separately by the caller
        using lookup_info_async() with page.run_task() for Flet apps.
        """
        with start_action(action_type="add_restaurant", name=name, category=category):
            try:
                self.db.add_restaurant_to_db(name, category)
                return f"Added restaurant: {name} ({category})"
            except ValueError:
                raise
            except Exception as e:
                raise Exception(f"Error adding restaurant: {str(e)}") from e

    def lookup_info_sync(self, restaurant_name: str) -> None:
        """Sync restaurant info lookup - call with page.run_thread().

        This method runs in a separate thread via Flet's page.run_thread(),
        creating its own event loop isolated from Flet's async context.
        """
        from app.backend.agent import lookup_restaurant_info
        from eliot import log_message

        log_message(message_type="bg_thread_started")
        with start_action(action_type="restaurant_lookup", restaurant=restaurant_name):
            try:
                log_message(message_type="bg_calling_lookup")
                info = lookup_restaurant_info(restaurant_name)
                log_message(message_type="bg_lookup_returned", found=info is not None)
                if info:
                    save_restaurant_info(
                        restaurant_name,
                        address=info.address,
                        phone=info.phone,
                        hours=info.hours,
                        website=info.website,
                        description=info.description,
                    )
                    log_message(message_type="bg_info_saved")
            except Exception as e:
                log_message(message_type="bg_lookup_error", error=str(e))

    def _lookup_info_background(self, restaurant_name: str) -> None:
        """Legacy sync background lookup for non-Flet contexts (e.g., tests)."""
        from app.backend.agent import lookup_restaurant_info
        from eliot import log_message

        def _do_lookup():
            log_message(message_type="bg_thread_entered")
            with start_action(action_type="restaurant_lookup", restaurant=restaurant_name):
                try:
                    log_message(message_type="bg_calling_lookup")
                    info = lookup_restaurant_info(restaurant_name)
                    log_message(message_type="bg_lookup_returned", found=info is not None)
                    if info:
                        save_restaurant_info(
                            restaurant_name,
                            address=info.address,
                            phone=info.phone,
                            hours=info.hours,
                            website=info.website,
                            description=info.description,
                        )
                        log_message(message_type="bg_info_saved")
                except Exception as e:
                    log_message(message_type="bg_lookup_error", error=str(e))

        thread = threading.Thread(target=_do_lookup, daemon=False)
        thread.start()

    def delete_restaurant(self, name: str) -> str:
        """
        Delete a restaurant from the database.
        Returns success message or raises exception.
        """
        with start_action(action_type="delete_restaurant", name=name):
            try:
                self.db.delete_restaurant_from_db(name)
                return f"Deleted restaurant: {name}"
            except ValueError:
                raise
            except Exception as e:
                raise Exception(f"Error deleting restaurant: {str(e)}") from e

    def select_restaurant(self, category: str = "Normal") -> tuple[str, str]:
        """
        Select a restaurant for lunch using round-robin logic.
        Returns the selected restaurant or raises exception.
        """
        with start_action(action_type="roll_lunch", category=category) as action:
            try:
                # Ensure category exists in session tracking
                if category not in self.session_rolled_restaurants:
                    self.session_rolled_restaurants[category] = set()

                restaurant = self.db.calculate_lunch(category, self.session_rolled_restaurants[category])
                action.add_success_fields(selected=restaurant[0])
                return restaurant
            except ValueError as e:
                if "No restaurants found" in str(e):
                    raise ValueError(f"No {category.lower()} restaurants available. Add some restaurants first!") from None
                else:
                    raise
            except Exception as e:
                raise Exception(f"Error selecting restaurant: {str(e)}") from e

    def get_random_restaurant(self, category: str) -> tuple[str, str]:
        """Get a random restaurant with the specified category."""
        try:
            return self.db.rng_restaurant(category)
        except ValueError:
            raise
        except Exception as e:
            raise Exception(f"Error getting random restaurant: {str(e)}") from e

    def reset_session_for_category(self, category: str) -> None:
        """Reset the session rolled restaurants for a specific category."""
        if category in self.session_rolled_restaurants:
            self.session_rolled_restaurants[category].clear()

    def reset_all_sessions(self) -> None:
        """Reset all session rolled restaurants."""
        for category in self.session_rolled_restaurants:
            self.session_rolled_restaurants[category].clear()
