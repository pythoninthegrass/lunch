"""
Unit tests for GUI layout spacing.

**Feature: basecoat-ui-refactor**
**Validates: Requirements 3.4**
"""

import flet as ft
import pytest
from app.frontend.gui import LunchGUI
from app.frontend.theme import SPACING
from unittest.mock import MagicMock, Mock


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
    return page


def test_button_row_uses_correct_spacing(mock_page):
    """
    Unit test: Verify button_row uses correct spacing from SPACING tokens.
    **Validates: Requirements 3.4**
    """
    # Create GUI instance
    gui = LunchGUI(mock_page)

    # Verify button_row exists
    assert hasattr(gui, "button_row"), "GUI missing button_row attribute"
    assert isinstance(gui.button_row, ft.Row), "button_row must be a ft.Row instance"

    # Verify spacing uses SPACING["sm"] token
    assert gui.button_row.spacing == SPACING["sm"], \
        f"button_row.spacing should be SPACING['sm'] ({SPACING['sm']}), got {gui.button_row.spacing}"

    # Verify run_spacing uses SPACING["sm"] token
    assert gui.button_row.run_spacing == SPACING["sm"], \
        f"button_row.run_spacing should be SPACING['sm'] ({SPACING['sm']}), got {gui.button_row.run_spacing}"


def test_add_restaurant_modal_uses_correct_spacing(mock_page):
    """
    Unit test: Verify add restaurant modal layout uses correct spacing from SPACING tokens.
    **Validates: Requirements 3.4**
    """
    # Create GUI instance
    gui = LunchGUI(mock_page)

    # Mock the callback to avoid errors
    gui.on_add_restaurant = Mock(return_value="Restaurant added")

    # Trigger the add restaurant sheet
    gui._show_add_restaurant_sheet()

    # Get the modal content
    modal_content = gui.bottom_sheet.content.content.controls[0]

    # Verify it's a Column
    assert isinstance(modal_content, ft.Column), "Modal content should be a ft.Column"

    # Verify the Column uses SPACING["md"] for spacing
    assert modal_content.spacing == SPACING["md"], \
        f"Add restaurant modal spacing should be SPACING['md'] ({SPACING['md']}), got {modal_content.spacing}"

    # Find the action button row (last control in the column)
    action_row = None
    for control in modal_content.controls:
        if isinstance(control, ft.Row):
            action_row = control

    assert action_row is not None, "Add restaurant modal should have an action button row"

    # Verify action row uses SPACING["sm"] for spacing
    assert action_row.spacing == SPACING["sm"], \
        f"Add restaurant modal action row spacing should be SPACING['sm'] ({SPACING['sm']}), got {action_row.spacing}"


def test_delete_restaurant_modal_uses_correct_spacing(mock_page):
    """
    Unit test: Verify delete restaurant modal layout uses correct spacing from SPACING tokens.
    **Validates: Requirements 3.4**
    """
    # Create GUI instance
    gui = LunchGUI(mock_page)

    # Mock the callbacks
    gui.on_get_all_restaurants = Mock(return_value=[
        ("Restaurant A", "cheap"),
        ("Restaurant B", "Normal"),
    ])
    gui.on_delete_restaurant = Mock(return_value="Restaurant deleted")

    # Trigger the delete restaurant sheet
    gui._show_delete_restaurant_sheet()

    # Get the modal content
    modal_content = gui.bottom_sheet.content.content.controls[0]

    # Verify it's a Column
    assert isinstance(modal_content, ft.Column), "Modal content should be a ft.Column"

    # Verify the Column uses SPACING["md"] for spacing
    assert modal_content.spacing == SPACING["md"], \
        f"Delete restaurant modal spacing should be SPACING['md'] ({SPACING['md']}), got {modal_content.spacing}"

    # Find the restaurant list container (second control in the main column)
    restaurant_list_container = modal_content.controls[1]

    assert isinstance(restaurant_list_container, ft.Container), "Restaurant list container should be a ft.Container"

    # Verify the ListView inside the container uses SPACING["sm"] for spacing
    list_view = restaurant_list_container.content
    assert isinstance(list_view, ft.ListView), "Container content should be a ft.ListView"
    assert list_view.spacing == SPACING["sm"], \
        f"Delete restaurant modal list spacing should be SPACING['sm'] ({SPACING['sm']}), got {list_view.spacing}"


def test_list_all_modal_uses_correct_spacing(mock_page):
    """
    Unit test: Verify list all modal layout uses correct spacing from SPACING tokens.
    **Validates: Requirements 3.4**
    """
    # Create GUI instance
    gui = LunchGUI(mock_page)

    # Mock the callback
    gui.on_get_all_restaurants = Mock(return_value=[
        ("Restaurant A", "cheap"),
        ("Restaurant B", "Normal"),
        ("Restaurant C", "cheap"),
    ])

    # Trigger the list all sheet
    gui._show_list_all_sheet()

    # Get the modal content
    modal_content = gui.bottom_sheet.content.content.controls[0]

    # Verify it's a Column
    assert isinstance(modal_content, ft.Column), "Modal content should be a ft.Column"

    # Verify the Column uses SPACING["md"] for spacing
    assert modal_content.spacing == SPACING["md"], \
        f"List all modal spacing should be SPACING['md'] ({SPACING['md']}), got {modal_content.spacing}"

    # Find the restaurant list container (second control in the main column)
    restaurant_list_container = modal_content.controls[1]

    assert isinstance(restaurant_list_container, ft.Container), "Restaurant list container should be a ft.Container"

    # Verify the ListView inside the container uses SPACING["sm"] for spacing
    list_view = restaurant_list_container.content
    assert isinstance(list_view, ft.ListView), "Container content should be a ft.ListView"
    assert list_view.spacing == SPACING["sm"], \
        f"List all modal list spacing should be SPACING['sm'] ({SPACING['sm']}), got {list_view.spacing}"


def test_radio_group_uses_correct_spacing(mock_page):
    """
    Unit test: Verify radio group uses correct spacing from SPACING tokens.
    **Validates: Requirements 3.4**
    """
    # Create GUI instance
    gui = LunchGUI(mock_page)

    # Verify radio_group exists
    assert hasattr(gui, "radio_group"), "GUI missing radio_group attribute"
    assert isinstance(gui.radio_group, ft.RadioGroup), "radio_group must be a ft.RadioGroup instance"

    # Get the Row inside the RadioGroup
    radio_row = gui.radio_group.content

    assert isinstance(radio_row, ft.Row), "RadioGroup content should be a ft.Row"

    # Verify spacing uses SPACING["sm"] token
    assert radio_row.spacing == SPACING["sm"], \
        f"radio_group Row spacing should be SPACING['sm'] ({SPACING['sm']}), got {radio_row.spacing}"


def test_radio_group_initial_state(mock_page):
    """
    Unit test: Verify radio group initial state is correct.
    **Validates: Requirements 4.5**
    """
    # Create GUI instance
    gui = LunchGUI(mock_page)

    # Verify radio_group exists
    assert hasattr(gui, "radio_group"), "GUI missing radio_group attribute"
    assert isinstance(gui.radio_group, ft.RadioGroup), "radio_group must be a ft.RadioGroup instance"

    # Verify initial value is "Normal"
    assert gui.radio_group.value == "Normal", \
        f"radio_group initial value should be 'Normal', got {gui.radio_group.value}"

    # Verify current_option is also initialized to "Normal"
    assert gui.current_option == "Normal", \
        f"current_option initial value should be 'Normal', got {gui.current_option}"


def test_radio_group_selection_updates_state(mock_page):
    """
    Unit test: Verify radio group selection updates current_option state.
    **Validates: Requirements 4.5**
    """
    # Create GUI instance
    gui = LunchGUI(mock_page)

    # Verify initial state
    assert gui.current_option == "Normal", "Initial state should be 'Normal'"

    # Create a mock event that simulates radio button change to "cheap"
    mock_event = Mock()
    mock_event.control = Mock()
    mock_event.control.value = "cheap"

    # Call the on_change handler
    gui._on_option_changed(mock_event)

    # Verify current_option was updated
    assert gui.current_option == "cheap", \
        f"current_option should be updated to 'cheap', got {gui.current_option}"

    # Create another mock event to change back to "Normal"
    mock_event.control.value = "Normal"
    gui._on_option_changed(mock_event)

    # Verify current_option was updated again
    assert gui.current_option == "Normal", \
        f"current_option should be updated to 'Normal', got {gui.current_option}"
