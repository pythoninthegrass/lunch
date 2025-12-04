"""
Frontend GUI module for the lunch application.
This module contains all Flet UI components and is decoupled from business logic.
"""

import flet as ft
from app.backend.logging import setup_logging
from collections.abc import Callable
from eliot import log_message

setup_logging()


class LunchGUI:
    """Main GUI class for the lunch application."""

    def __init__(self, page: ft.Page):
        """Initialize the GUI with a Flet page."""
        self.page = page
        self.setup_page()
        self.create_controls()
        self.setup_layout()

        # Callbacks for backend communication
        self.on_roll_lunch: Callable[[str], str] | None = None
        self.on_add_restaurant: Callable[[str, str], str] | None = None
        self.on_delete_restaurant: Callable[[str], str] | None = None
        self.on_get_all_restaurants: Callable[[], list[tuple[str, str]]] | None = None

    def setup_page(self):
        """Configure the main page settings."""
        self.page.title = "Lunch"
        self.page.window_width = 800
        self.page.window_height = 400
        self.page.vertical_alignment = "center"
        self.page.horizontal_alignment = "center"
        self.page.padding = 10
        self.page.background_color = ft.Colors.WHITE

    def create_controls(self):
        """Create all UI controls."""
        # Banner image
        self.banner_image = ft.Container(
            content=ft.Image(
                src="banner.png",
                width=500,
                fit=ft.ImageFit.CONTAIN,
            ),
            shadow=None,
        )

        # Text controls
        self.title_text = ft.Text("Click below to find out what's for Lunch:")
        self.result_text = ft.Text()

        # Default option
        self.current_option = "Normal"

        # Radio button group for category selection
        self.radio_group = ft.RadioGroup(
            content=ft.Row(
                [
                    ft.Container(
                        ft.Radio(value="cheap", label="Cheap"),
                        alignment=ft.Alignment(0.0, 0.0),
                    ),
                    ft.Container(
                        ft.Radio(value="Normal", label="Normal"),
                        alignment=ft.Alignment(0.0, 0.0),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            value="Normal",
            on_change=self._on_option_changed,
        )

        # Bottom sheet for modal dialogs
        self.bottom_sheet = ft.BottomSheet(
            ft.Container(
                ft.Column(
                    [
                        ft.Text("", size=16),
                        ft.ElevatedButton("Close", on_click=lambda e: self._close_bottom_sheet()),
                    ],
                    tight=True,
                ),
                padding=10,
            ),
            open=False,
        )
        self.page.overlay.append(self.bottom_sheet)

        # Action buttons
        self.button_row = ft.Row(
            controls=[
                ft.Container(
                    ft.ElevatedButton("Roll Lunch", on_click=self._on_roll_lunch_clicked),
                    alignment=ft.Alignment(0.0, 0.0),
                ),
                ft.Container(
                    ft.ElevatedButton(
                        "Delete Restaurant",
                        on_click=lambda e: self._show_delete_restaurant_sheet(),
                    ),
                    alignment=ft.Alignment(0.0, 0.0),
                ),
                ft.Container(
                    ft.ElevatedButton(
                        "Add Restaurant",
                        on_click=lambda e: self._show_add_restaurant_sheet(),
                    ),
                    alignment=ft.Alignment(0.0, 0.0),
                ),
                ft.Container(
                    ft.ElevatedButton("List All", on_click=lambda e: self._show_list_all_sheet()),
                    alignment=ft.Alignment(0.0, 0.0),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

    def setup_layout(self):
        """Add all controls to the page."""
        self.page.add(self.banner_image, self.title_text, self.radio_group, self.button_row, self.result_text)

    def set_callbacks(
        self,
        roll_lunch_callback: Callable[[str], str],
        add_restaurant_callback: Callable[[str, str], str],
        delete_restaurant_callback: Callable[[str], str],
        get_all_restaurants_callback: Callable[[], list[tuple[str, str]]],
    ):
        """Set callbacks for backend communication."""
        self.on_roll_lunch = roll_lunch_callback
        self.on_add_restaurant = add_restaurant_callback
        self.on_delete_restaurant = delete_restaurant_callback
        self.on_get_all_restaurants = get_all_restaurants_callback

    def update_result(self, message: str):
        """Update the result text display."""
        self.result_text.value = message
        self.page.update()

    def _on_option_changed(self, e):
        """Handle option radio button change."""
        self.current_option = e.control.value
        log_message(message_type="ui_radio_changed", option=self.current_option)
        self.page.update()

    def _close_bottom_sheet(self):
        """Close the bottom sheet modal."""
        self.bottom_sheet.open = False
        self.page.update()

    def _on_roll_lunch_clicked(self, e):
        """Handle roll lunch button click."""
        log_message(message_type="ui_button_click", button="roll_lunch", option=self.current_option)
        if self.on_roll_lunch:
            try:
                result = self.on_roll_lunch(self.current_option)
                self.update_result(f"Today's lunch: {result}")
            except Exception as ex:
                self.update_result(str(ex))

    def _show_add_restaurant_sheet(self):
        """Show the add restaurant modal."""
        log_message(message_type="ui_button_click", button="add_restaurant")
        entry_field = ft.TextField(label="Restaurant Name")

        def on_add_radio_changed(e):
            log_message(message_type="ui_radio_changed", context="add_restaurant", option=e.control.value)

        option_radio = ft.RadioGroup(
            content=ft.Row(
                [
                    ft.Radio(value="cheap", label="Cheap"),
                    ft.Radio(value="Normal", label="Normal"),
                ]
            ),
            value="Normal",
            on_change=on_add_radio_changed,
        )

        def add_restaurant_confirm(e):
            restaurant_name = entry_field.value
            if not restaurant_name:
                return

            log_message(message_type="ui_button_click", button="add_confirm", name=restaurant_name, category=option_radio.value)
            if self.on_add_restaurant:
                try:
                    result = self.on_add_restaurant(restaurant_name, option_radio.value)
                    self.update_result(result)
                    self._close_bottom_sheet()
                except Exception as ex:
                    self.update_result(str(ex))

        # Update bottom sheet content
        self.bottom_sheet.content.content.controls = [
            ft.Column(
                [
                    ft.Text("Add New Restaurant", size=16, weight="bold"),
                    entry_field,
                    ft.Text("Price Range:"),
                    option_radio,
                    ft.Row(
                        [
                            ft.ElevatedButton("Cancel", on_click=lambda e: self._close_bottom_sheet()),
                            ft.ElevatedButton("Add", on_click=add_restaurant_confirm),
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ],
                tight=True,
            )
        ]

        self.bottom_sheet.open = True
        self.page.update()

    def _show_delete_restaurant_sheet(self):
        """Show the delete restaurant modal."""
        log_message(message_type="ui_button_click", button="delete_restaurant")
        if not self.on_get_all_restaurants:
            return

        try:
            restaurants = self.on_get_all_restaurants()
        except Exception as ex:
            self.update_result(f"Error getting restaurants: {str(ex)}")
            return

        def delete_restaurant_confirm(restaurant):
            log_message(message_type="ui_button_click", button="delete_confirm", name=restaurant[0])
            if self.on_delete_restaurant:
                try:
                    result = self.on_delete_restaurant(restaurant[0])
                    self.update_result(result)
                    self._close_bottom_sheet()
                except Exception as ex:
                    self.update_result(str(ex))

        # Create restaurant buttons
        restaurant_buttons = []
        for restaurant in restaurants:
            restaurant_buttons.append(
                ft.ElevatedButton(
                    f"{restaurant[0]} ({restaurant[1]})",
                    on_click=lambda e, r=restaurant: delete_restaurant_confirm(r),
                    data=restaurant,
                )
            )

        # Update bottom sheet content
        self.bottom_sheet.content.content.controls = [
            ft.Column(
                [
                    ft.Text("Select Restaurant to Delete", size=16, weight="bold"),
                    ft.Column(restaurant_buttons, scroll=True, height=300),
                    ft.ElevatedButton("Cancel", on_click=lambda e: self._close_bottom_sheet()),
                ],
                tight=True,
            )
        ]

        self.bottom_sheet.open = True
        self.page.update()

    def _show_list_all_sheet(self):
        """Show the list all restaurants modal."""
        log_message(message_type="ui_button_click", button="list_all")
        if not self.on_get_all_restaurants:
            return

        try:
            restaurants = self.on_get_all_restaurants()
        except Exception as ex:
            self.update_result(f"Error getting restaurants: {str(ex)}")
            return

        # Create restaurant items
        restaurant_items = []
        for restaurant in restaurants:
            restaurant_items.append(ft.Text(f"{restaurant[0]} ({restaurant[1]})"))

        # Update bottom sheet content
        self.bottom_sheet.content.content.controls = [
            ft.Column(
                [
                    ft.Text("All Restaurants", size=16, weight="bold"),
                    ft.Column(restaurant_items, scroll=True, height=300),
                    ft.ElevatedButton("Close", on_click=lambda e: self._close_bottom_sheet()),
                ],
                tight=True,
            )
        ]

        self.bottom_sheet.open = True
        self.page.update()


def create_gui(page: ft.Page) -> LunchGUI:
    """Factory function to create and return a LunchGUI instance."""
    return LunchGUI(page)
