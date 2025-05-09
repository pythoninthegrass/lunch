import flet as ft
from utils.db import (
    add_restaurant_to_db,
    calculate_lunch,
    create_db_and_tables,
    delete_restaurant_from_db,
    get_all_restaurants,
    rng_restaurant,
)


def create_app(page: ft.Page):
    page.title = "Lunch"
    page.window_width = 650
    page.window_height = 400
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"
    page.padding = 10
    page.background_color = ft.Colors.WHITE

    # Create database and tables if they don't exist
    create_db_and_tables()

    # Create text controls
    title_text = ft.Text("Click below to find out what's for Lunch:")
    result_text = ft.Text()

    # Create radio button group for options
    option = "Normal"  # Default option

    def option_changed(e):
        nonlocal option
        option = e.control.value
        page.update()

    radio_group = ft.RadioGroup(
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
        on_change=option_changed,
    )

    # Bottom sheet for adding/deleting restaurants
    bottom_sheet = ft.BottomSheet(
        ft.Container(
            ft.Column(
                [
                    ft.Text("", size=16),
                    ft.ElevatedButton("Close", on_click=lambda e: close_bs()),
                ],
                tight=True,
            ),
            padding=10,
        ),
        open=False,
    )
    page.overlay.append(bottom_sheet)

    # Methods for bottom sheet operations
    def close_bs():
        bottom_sheet.open = False
        page.update()

    def show_add_restaurant_sheet():
        entry_field = ft.TextField(label="Restaurant Name")

        def add_restaurant_confirm(e, opt):
            try:
                restaurant_name = entry_field.value
                if not restaurant_name:
                    return

                # Add restaurant to database
                add_restaurant_to_db(restaurant_name, opt or option)

                # Show a confirmation
                result_text.value = (
                    f"Added restaurant: {restaurant_name} ({opt or option})"
                )

                # Close the bottom sheet
                close_bs()
                page.update()
            except Exception as e:
                result_text.value = f"Error adding restaurant: {str(e)}"
                page.update()

        option_radio = ft.RadioGroup(
            content=ft.Row(
                [
                    ft.Radio(value="cheap", label="Cheap"),
                    ft.Radio(value="Normal", label="Normal"),
                ]
            ),
            value="Normal",
        )

        # Update bottom sheet content
        bottom_sheet.content.content.controls = [
            ft.Column(
                [
                    ft.Text("Add New Restaurant", size=16, weight="bold"),
                    entry_field,
                    ft.Text("Price Range:"),
                    option_radio,
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "Add",
                                on_click=lambda e: add_restaurant_confirm(
                                    e, option_radio.value
                                ),
                            ),
                            ft.ElevatedButton("Cancel", on_click=lambda e: close_bs()),
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ],
                tight=True,
            )
        ]

        bottom_sheet.open = True
        page.update()

    def show_delete_restaurant_sheet():
        # Get all restaurants from the database
        restaurants = get_all_restaurants()

        def delete_restaurant_confirm(e, restaurant):
            try:
                # Delete restaurant from database
                delete_restaurant_from_db(restaurant[0])

                # Show a confirmation
                result_text.value = f"Deleted restaurant: {restaurant[0]}"

                # Close the bottom sheet
                close_bs()
                page.update()
            except Exception as e:
                result_text.value = f"Error deleting restaurant: {str(e)}"
                page.update()

        # Create a column with all restaurants as buttons
        restaurant_buttons = []
        for restaurant in restaurants:
            restaurant_buttons.append(
                ft.ElevatedButton(
                    text=f"{restaurant[0]} ({restaurant[1]})",
                    on_click=lambda e, r=restaurant: delete_restaurant_confirm(e, r),
                    data=restaurant,
                )
            )

        # Update bottom sheet content
        bottom_sheet.content.content.controls = [
            ft.Column(
                [
                    ft.Text("Select Restaurant to Delete", size=16, weight="bold"),
                    ft.Column(restaurant_buttons, scroll=True, height=300),
                    ft.ElevatedButton("Cancel", on_click=lambda e: close_bs()),
                ],
                tight=True,
            )
        ]

        bottom_sheet.open = True
        page.update()

    def show_list_all_sheet():
        # Get all restaurants from the database
        restaurants = get_all_restaurants()

        # Create a column with all restaurants
        restaurant_items = []
        for restaurant in restaurants:
            restaurant_items.append(ft.Text(f"{restaurant[0]} ({restaurant[1]})"))

        # Update bottom sheet content
        bottom_sheet.content.content.controls = [
            ft.Column(
                [
                    ft.Text("All Restaurants", size=16, weight="bold"),
                    ft.Column(restaurant_items, scroll=True, height=300),
                    ft.ElevatedButton("Close", on_click=lambda e: close_bs()),
                ],
                tight=True,
            )
        ]

        bottom_sheet.open = True
        page.update()

    def roll_lunch(e):
        """Select a restaurant for lunch based on the selected option and history"""
        try:
            # Get calculated restaurant from database
            restaurant = calculate_lunch(option)

            # Update the result text
            result_text.value = f"Today's lunch: {restaurant[0]}"
            page.update()
        except Exception as e:
            # Handle error (e.g., no restaurants found)
            result_text.value = f"Error selecting restaurant: {str(e)}"
            page.update()

    # Create action buttons
    button_row = ft.Row(
        controls=[
            ft.Container(
                ft.ElevatedButton(text="Roll Lunch", on_click=roll_lunch),
                alignment=ft.Alignment(0.0, 0.0),
            ),
            ft.Container(
                ft.ElevatedButton(
                    text="Delete Restaurant",
                    on_click=lambda e: show_delete_restaurant_sheet(),
                ),
                alignment=ft.Alignment(0.0, 0.0),
            ),
            ft.Container(
                ft.ElevatedButton(
                    text="Add Restaurant",
                    on_click=lambda e: show_add_restaurant_sheet(),
                ),
                alignment=ft.Alignment(0.0, 0.0),
            ),
            ft.Container(
                ft.ElevatedButton(
                    text="List All", on_click=lambda e: show_list_all_sheet()
                ),
                alignment=ft.Alignment(0.0, 0.0),
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # Add all controls to the page
    page.add(title_text, radio_group, button_row, result_text)
