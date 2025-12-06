"""
Integration tests for GUI functionality.
Tests the complete flow from GUI interactions to backend operations.

**Feature: basecoat-ui-refactor**
"""

import flet as ft
import pytest
import sqlite3
import tempfile
from app.backend.service import RestaurantService
from app.frontend.gui import LunchGUI
from unittest.mock import Mock, patch


class RealDatabaseManager:
    """Real database manager for integration testing."""

    def create_db_and_tables(self):
        from app.backend.db import create_db_and_tables

        return create_db_and_tables()

    def get_all_restaurants(self):
        from app.backend.db import get_all_restaurants

        return get_all_restaurants()

    def get_restaurants(self, option):
        from app.backend.db import get_restaurants

        return get_restaurants(option)

    def add_restaurant_to_db(self, name, option):
        from app.backend.db import add_restaurant_to_db

        return add_restaurant_to_db(name, option)

    def delete_restaurant_from_db(self, name):
        from app.backend.db import delete_restaurant_from_db

        return delete_restaurant_from_db(name)

    def calculate_lunch(self, option, session_rolled):
        from app.backend.db import calculate_lunch

        return calculate_lunch(option, session_rolled)

    def rng_restaurant(self, option):
        from app.backend.db import rng_restaurant

        return rng_restaurant(option)


@pytest.fixture
def mock_page():
    """Create a mock Flet page for testing."""
    page = Mock(spec=ft.Page)
    page.overlay = []
    page.controls = []
    page.update = Mock()
    page.add = Mock()
    page.theme_mode = ft.ThemeMode.LIGHT
    page.platform = "web"
    page.window_height = 400
    page.window_width = 800
    return page


@pytest.fixture
def test_db_setup():
    """Setup a temporary test database with sample data."""
    # Create a temporary database
    temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_db_path = temp_file.name
    temp_file.close()

    # Create fresh database with sample data
    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS lunch_list (
        restaurants TEXT PRIMARY KEY,
        option TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recent_lunch (
        restaurants TEXT PRIMARY KEY,
        date TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS restaurant_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        restaurant_name TEXT NOT NULL UNIQUE,
        address TEXT,
        phone TEXT,
        hours TEXT,
        website TEXT,
        description TEXT,
        last_updated TEXT,
        FOREIGN KEY (restaurant_name) REFERENCES lunch_list(restaurants)
            ON DELETE CASCADE
    )
    ''')

    # Insert sample data
    sample_data = [
        ("McDonald's", "cheap"),
        ("Burger King", "cheap"),
        ("Subway", "cheap"),
        ("The Ritz", "Normal"),
        ("Fine Dining", "Normal"),
        ("Steakhouse", "Normal"),
    ]

    cursor.executemany("INSERT INTO lunch_list VALUES (?, ?)", sample_data)
    conn.commit()
    conn.close()

    # Start the patch
    patcher = patch('app.backend.db.db_path', temp_db_path)
    patcher.start()

    yield temp_db_path

    # Cleanup
    patcher.stop()
    import os

    if os.path.exists(temp_db_path):
        os.unlink(temp_db_path)


class TestGUIIntegration:
    """Integration tests for GUI functionality with real backend."""

    def test_roll_lunch_functionality(self, mock_page, test_db_setup):
        """
        Integration test: Verify clicking "Roll Lunch" executes callback and displays result.
        **Validates: Requirements 4.1**
        """
        # Setup service with real database
        db_manager = RealDatabaseManager()
        service = RestaurantService(db_manager)
        service.initialize()

        # Create GUI
        gui = LunchGUI(mock_page)

        # Wire up callbacks
        gui.set_callbacks(
            roll_lunch_callback=lambda category: service.select_restaurant(category)[0],
            add_restaurant_callback=service.add_restaurant,
            delete_restaurant_callback=service.delete_restaurant,
            get_all_restaurants_callback=service.get_all_restaurants,
        )

        # Verify initial state
        assert gui.result_text.value is None or gui.result_text.value == ""

        # Simulate clicking "Roll Lunch" button
        # Find the roll lunch button (first button in button_row)
        roll_button = gui.button_row.controls[0]
        assert "Roll Lunch" in roll_button.text

        # Create mock event
        mock_event = Mock()

        # Click the button
        roll_button.on_click(mock_event)

        # Verify result was updated
        assert gui.result_text.value.startswith("Today's lunch:")
        assert len(gui.result_text.value) > len("Today's lunch:")

        # Verify the selected restaurant is from the correct category
        selected_restaurant = gui.result_text.value.replace("Today's lunch: ", "")
        all_restaurants = service.get_all_restaurants()
        restaurant_names = [r[0] for r in all_restaurants]
        assert selected_restaurant in restaurant_names

    def test_roll_lunch_respects_category_selection(self, mock_page, test_db_setup):
        """
        Integration test: Verify roll lunch respects the selected category.
        **Validates: Requirements 4.1, 4.5**
        """
        # Setup service with real database
        db_manager = RealDatabaseManager()
        service = RestaurantService(db_manager)
        service.initialize()

        # Create GUI
        gui = LunchGUI(mock_page)

        # Wire up callbacks
        gui.set_callbacks(
            roll_lunch_callback=lambda category: service.select_restaurant(category)[0],
            add_restaurant_callback=service.add_restaurant,
            delete_restaurant_callback=service.delete_restaurant,
            get_all_restaurants_callback=service.get_all_restaurants,
        )

        # Change category to "cheap"
        mock_event = Mock()
        mock_event.control = Mock()
        mock_event.control.value = "cheap"
        gui._on_option_changed(mock_event)

        # Verify category was updated
        assert gui.current_option == "cheap"

        # Click roll lunch
        roll_button = gui.button_row.controls[0]
        roll_button.on_click(Mock())

        # Verify result contains a cheap restaurant
        selected_restaurant = gui.result_text.value.replace("Today's lunch: ", "")
        cheap_restaurants = service.get_restaurants_by_category("cheap")
        cheap_names = [r[0] for r in cheap_restaurants]
        assert selected_restaurant in cheap_names

    def test_add_restaurant_functionality(self, mock_page, test_db_setup):
        """
        Integration test: Verify add dialog opens, accepts input, and persists to database.
        **Validates: Requirements 4.2**
        """
        # Setup service with real database
        db_manager = RealDatabaseManager()
        service = RestaurantService(db_manager)
        service.initialize()

        # Create GUI
        gui = LunchGUI(mock_page)

        # Wire up callbacks
        gui.set_callbacks(
            roll_lunch_callback=lambda category: service.select_restaurant(category)[0],
            add_restaurant_callback=service.add_restaurant,
            delete_restaurant_callback=service.delete_restaurant,
            get_all_restaurants_callback=service.get_all_restaurants,
        )

        # Get initial restaurant count
        initial_restaurants = service.get_all_restaurants()
        initial_count = len(initial_restaurants)

        # Open add restaurant dialog
        gui._show_add_restaurant_sheet()

        # Verify bottom sheet is open
        assert gui.bottom_sheet.open is True

        # Get the modal content
        modal_content = gui.bottom_sheet.content.content.controls[0]
        assert isinstance(modal_content, ft.Column)

        # Find the text field (second control in the column)
        text_field = modal_content.controls[1]
        assert isinstance(text_field, ft.TextField)

        # Set restaurant name
        text_field.value = "Integration Test Restaurant"

        # Find the radio group (fifth control in the column, after warning_text)
        radio_group = modal_content.controls[4]
        assert isinstance(radio_group, ft.RadioGroup)

        # Set category to "Normal"
        radio_group.value = "Normal"

        # Find the action row (last control in the column)
        action_row = modal_content.controls[5]
        assert isinstance(action_row, ft.Row)

        # Find the "Add" button (second button in the action row)
        add_button = action_row.controls[1]
        assert "Add" in add_button.text

        # Click the add button
        mock_event = Mock()
        add_button.on_click(mock_event)

        # Verify restaurant was added to database
        updated_restaurants = service.get_all_restaurants()
        assert len(updated_restaurants) == initial_count + 1

        # Verify the new restaurant is in the list
        restaurant_names = [r[0] for r in updated_restaurants]
        assert "Integration Test Restaurant" in restaurant_names

        # Verify result message was updated
        assert "Added restaurant: Integration Test Restaurant" in gui.result_text.value

        # Verify bottom sheet was closed
        assert gui.bottom_sheet.open is False

    def test_delete_restaurant_functionality(self, mock_page, test_db_setup):
        """
        Integration test: Verify delete dialog shows restaurants and removes selected one.
        **Validates: Requirements 4.3**
        """
        # Setup service with real database
        db_manager = RealDatabaseManager()
        service = RestaurantService(db_manager)
        service.initialize()

        # Create GUI
        gui = LunchGUI(mock_page)

        # Wire up callbacks
        gui.set_callbacks(
            roll_lunch_callback=lambda category: service.select_restaurant(category)[0],
            add_restaurant_callback=service.add_restaurant,
            delete_restaurant_callback=service.delete_restaurant,
            get_all_restaurants_callback=service.get_all_restaurants,
        )

        # Get initial restaurant count
        initial_restaurants = service.get_all_restaurants()
        initial_count = len(initial_restaurants)
        assert initial_count > 0

        # Pick a restaurant to delete
        restaurant_to_delete = initial_restaurants[0]

        # Open delete restaurant dialog
        gui._show_delete_restaurant_sheet()

        # Verify bottom sheet is open
        assert gui.bottom_sheet.open is True

        # Get the modal content
        modal_content = gui.bottom_sheet.content.content.controls[0]
        assert isinstance(modal_content, ft.Column)

        # Find the restaurant list container (second control in the column)
        list_container = modal_content.controls[1]
        assert isinstance(list_container, ft.Container)

        # Get the ListView
        list_view = list_container.content
        assert isinstance(list_view, ft.ListView)

        # Verify restaurants are displayed
        assert len(list_view.controls) == initial_count

        # Find the button for the restaurant we want to delete
        delete_button = None
        for button in list_view.controls:
            if restaurant_to_delete[0] in button.text:
                delete_button = button
                break

        assert delete_button is not None

        # Click the delete button
        mock_event = Mock()
        delete_button.on_click(mock_event)

        # Verify restaurant was deleted from database
        updated_restaurants = service.get_all_restaurants()
        assert len(updated_restaurants) == initial_count - 1

        # Verify the restaurant is no longer in the list
        restaurant_names = [r[0] for r in updated_restaurants]
        assert restaurant_to_delete[0] not in restaurant_names

        # Verify result message was updated
        assert f"Deleted restaurant: {restaurant_to_delete[0]}" in gui.result_text.value

        # Verify bottom sheet was closed
        assert gui.bottom_sheet.open is False

    def test_list_all_functionality(self, mock_page, test_db_setup):
        """
        Integration test: Verify list dialog displays all restaurants in scrollable view.
        **Validates: Requirements 4.4**
        """
        # Setup service with real database
        db_manager = RealDatabaseManager()
        service = RestaurantService(db_manager)
        service.initialize()

        # Create GUI
        gui = LunchGUI(mock_page)

        # Wire up callbacks
        gui.set_callbacks(
            roll_lunch_callback=lambda category: service.select_restaurant(category)[0],
            add_restaurant_callback=service.add_restaurant,
            delete_restaurant_callback=service.delete_restaurant,
            get_all_restaurants_callback=service.get_all_restaurants,
        )

        # Get all restaurants from database
        all_restaurants = service.get_all_restaurants()
        restaurant_count = len(all_restaurants)

        # Open list all dialog
        gui._show_list_all_sheet()

        # Verify bottom sheet is open
        assert gui.bottom_sheet.open is True

        # Get the modal content
        modal_content = gui.bottom_sheet.content.content.controls[0]
        assert isinstance(modal_content, ft.Column)

        # Find the restaurant list container (second control in the column)
        list_container = modal_content.controls[1]
        assert isinstance(list_container, ft.Container)

        # Get the ListView
        list_view = list_container.content
        assert isinstance(list_view, ft.ListView)

        # Verify all restaurants are displayed
        assert len(list_view.controls) == restaurant_count

        # Verify each restaurant is displayed with correct format
        displayed_restaurants = []
        for text_control in list_view.controls:
            assert isinstance(text_control, ft.Text)
            displayed_restaurants.append(text_control.value)

        # Check that all restaurants from database are displayed
        for restaurant in all_restaurants:
            expected_text = f"{restaurant[0]} ({restaurant[1]})"
            assert expected_text in displayed_restaurants

        # Find the close button (last control in the column)
        close_button = modal_content.controls[2]
        assert "Close" in close_button.text

        # Click the close button
        mock_event = Mock()
        close_button.on_click(mock_event)

        # Verify bottom sheet was closed
        assert gui.bottom_sheet.open is False

    def test_add_restaurant_with_empty_name(self, mock_page, test_db_setup):
        """
        Integration test: Verify add dialog handles empty restaurant name gracefully.
        **Validates: Requirements 4.2**
        """
        # Setup service with real database
        db_manager = RealDatabaseManager()
        service = RestaurantService(db_manager)
        service.initialize()

        # Create GUI
        gui = LunchGUI(mock_page)

        # Wire up callbacks
        gui.set_callbacks(
            roll_lunch_callback=lambda category: service.select_restaurant(category)[0],
            add_restaurant_callback=service.add_restaurant,
            delete_restaurant_callback=service.delete_restaurant,
            get_all_restaurants_callback=service.get_all_restaurants,
        )

        # Get initial restaurant count
        initial_count = len(service.get_all_restaurants())

        # Open add restaurant dialog
        gui._show_add_restaurant_sheet()

        # Get the modal content
        modal_content = gui.bottom_sheet.content.content.controls[0]

        # Find the text field
        text_field = modal_content.controls[1]

        # Leave text field empty
        text_field.value = ""

        # Find the "Add" button (action_row is at index 5 after warning_text was added)
        action_row = modal_content.controls[5]
        add_button = action_row.controls[1]

        # Click the add button
        mock_event = Mock()
        add_button.on_click(mock_event)

        # Verify no restaurant was added
        updated_count = len(service.get_all_restaurants())
        assert updated_count == initial_count

        # Verify bottom sheet is still open (since validation failed)
        assert gui.bottom_sheet.open is True

    def test_roll_lunch_with_no_restaurants(self, mock_page, test_db_setup):
        """
        Integration test: Verify roll lunch handles empty category gracefully.
        **Validates: Requirements 4.1**
        """
        # Setup service with real database
        db_manager = RealDatabaseManager()
        service = RestaurantService(db_manager)
        service.initialize()

        # Create GUI
        gui = LunchGUI(mock_page)

        # Wire up callbacks
        gui.set_callbacks(
            roll_lunch_callback=lambda category: service.select_restaurant(category)[0],
            add_restaurant_callback=service.add_restaurant,
            delete_restaurant_callback=service.delete_restaurant,
            get_all_restaurants_callback=service.get_all_restaurants,
        )

        # Delete all cheap restaurants
        cheap_restaurants = service.get_restaurants_by_category("cheap")
        for restaurant in cheap_restaurants:
            service.delete_restaurant(restaurant[0])

        # Change category to "cheap"
        mock_event = Mock()
        mock_event.control = Mock()
        mock_event.control.value = "cheap"
        gui._on_option_changed(mock_event)

        # Click roll lunch
        roll_button = gui.button_row.controls[0]
        roll_button.on_click(Mock())

        # Verify error message is displayed
        assert "No cheap restaurants available" in gui.result_text.value

    def test_add_restaurant_shows_warning_for_similar_name(self, mock_page, test_db_setup):
        """
        Integration test: Verify warning is shown when adding a restaurant with a similar name.
        **Validates: Requirements 4.2**
        """
        # Setup service with real database
        db_manager = RealDatabaseManager()
        service = RestaurantService(db_manager)
        service.initialize()

        # Add existing restaurant
        service.add_restaurant("Taco Bell", "cheap")

        # Create GUI
        gui = LunchGUI(mock_page)

        # Wire up callbacks
        gui.set_callbacks(
            roll_lunch_callback=lambda category: service.select_restaurant(category)[0],
            add_restaurant_callback=service.add_restaurant,
            delete_restaurant_callback=service.delete_restaurant,
            get_all_restaurants_callback=service.get_all_restaurants,
        )

        # Open add restaurant dialog
        gui._show_add_restaurant_sheet()

        # Get the modal content
        modal_content = gui.bottom_sheet.content.content.controls[0]
        assert isinstance(modal_content, ft.Column)

        # Find the text field (second control in the column)
        text_field = modal_content.controls[1]
        assert isinstance(text_field, ft.TextField)

        # Find the warning text (third control in the column)
        warning_text = modal_content.controls[2]
        assert isinstance(warning_text, ft.Text)

        # Warning should be hidden initially
        assert warning_text.visible is False

        # Simulate typing a similar name by calling on_change handler
        text_field.value = "TacoBell"
        mock_event = Mock()
        mock_event.control = text_field
        text_field.on_change(mock_event)

        # Warning should now be visible with similar name message
        assert warning_text.visible is True
        assert "similar" in warning_text.value.lower()
        assert "Taco Bell" in warning_text.value
