"""
Frontend GUI module for the lunch application.
This module contains all Flet UI components and is decoupled from business logic.
"""

import contextlib
import flet as ft
import re
from app.backend.logging import setup_logging
from app.frontend.theme import (
    BORDER_RADIUS,
    DARK_COLORS,
    LIGHT_COLORS,
    NAV_BAR_HEIGHT,
    SPACING,
    BasecoatTheme,
    apply_theme_mode,
    create_nav_bar,
    create_outline_button,
    create_primary_button,
    create_styled_textfield,
    get_colors,
)
from collections.abc import Callable
from eliot import log_message

setup_logging()


def normalize_name(name: str) -> str:
    """Normalize a restaurant name for similarity comparison.

    Removes spaces, apostrophes, and other punctuation, then lowercases.
    """
    return re.sub(r"[^a-z0-9]", "", name.lower())


class LunchGUI:
    """Main GUI class for the lunch application with bottom navigation."""

    # Navigation items configuration
    NAV_ITEMS = [
        {"icon": ft.Icons.HOME, "label": "Home", "view": "home"},
        {"icon": ft.Icons.ADD, "label": "Add", "view": "add"},
        {"icon": ft.Icons.LIST, "label": "List", "view": "list"},
        {"icon": ft.Icons.SETTINGS, "label": "Settings", "view": "settings"},
    ]

    def __init__(self, page: ft.Page):
        """Initialize the GUI with a Flet page."""
        self.page = page
        self.current_view = "home"
        self.active_nav_index = 0
        self.is_dark_mode = False
        self.match_system_theme = True
        self.views: dict[str, ft.Container] = {}

        # Callbacks for backend communication
        self.on_roll_lunch: Callable[[str], str] | None = None
        self.on_add_restaurant: Callable[[str, str], str] | None = None
        self.on_delete_restaurant: Callable[[str], str] | None = None
        self.on_get_all_restaurants: Callable[[], list[tuple[str, str]]] | None = None

        # Load saved theme preference
        self._load_theme_preference()

        # Apply theme and setup
        apply_theme_mode(self.page, self.is_dark_mode)
        self._setup_page()
        self._build_layout()

    def _load_theme_preference(self):
        """Load theme preference from client storage."""
        try:
            # Load match system theme setting (default: True)
            match_system = self.page.client_storage.get("match_system_theme")
            self.match_system_theme = match_system != "false"

            if self.match_system_theme:
                # Detect system theme
                self.is_dark_mode = self._detect_system_theme()
            else:
                # Use saved manual preference
                saved_theme = self.page.client_storage.get("theme_mode")
                if saved_theme == "dark":
                    self.is_dark_mode = True
        except Exception:
            pass

    def _detect_system_theme(self) -> bool:
        """Detect system dark mode preference."""
        try:
            return self.page.platform_brightness == ft.Brightness.DARK
        except Exception:
            return False

    def _save_theme_preference(self):
        """Save theme preference to client storage."""
        try:
            self.page.client_storage.set("match_system_theme", "true" if self.match_system_theme else "false")
            self.page.client_storage.set("theme_mode", "dark" if self.is_dark_mode else "light")
        except Exception:
            pass

    def _setup_page(self):
        """Configure the main page settings."""
        self.page.title = "Lunch"
        self.page.padding = 0
        self.page.spacing = 0

    def _build_layout(self):
        """Build the main layout with content area and bottom nav."""
        # Create all views
        self.views = {
            "home": self._create_home_view(),
            "add": self._create_add_view(),
            "list": self._create_list_view(),
            "settings": self._create_settings_view(),
        }

        # Theme toggle icon button (top-right, only visible on home page)
        self.theme_toggle_btn = self._create_theme_toggle_button()

        # Header row with theme toggle aligned to the right
        self.header_row = ft.Container(
            content=ft.Row(
                controls=[self.theme_toggle_btn],
                alignment=ft.MainAxisAlignment.END,
            ),
            padding=ft.padding.only(right=SPACING["sm"], top=SPACING["sm"]),
            height=48,
            visible=self.current_view == "home",
        )

        # Content area - stack all views, control visibility
        self.content_area = ft.Container(
            content=ft.Stack(
                controls=list(self.views.values()),
                expand=True,
            ),
            expand=True,
            padding=SPACING["md"],
        )

        # Navigation bar
        self.nav_bar = self._build_nav_bar()

        # Main layout
        self.page.add(
            ft.Column(
                controls=[
                    self.header_row,
                    self.content_area,
                    self.nav_bar,
                ],
                spacing=0,
                expand=True,
            )
        )

        # Set initial view visibility
        self._switch_view("home")

    def _build_nav_bar(self) -> ft.Container:
        """Build the bottom navigation bar."""
        return create_nav_bar(
            items=self.NAV_ITEMS,
            active_index=self.active_nav_index,
            on_change=self._on_nav_change,
            is_dark=self.is_dark_mode,
        )

    def _rebuild_nav_bar(self):
        """Rebuild nav bar (e.g., after theme change)."""
        new_nav = self._build_nav_bar()
        # Find and replace nav bar in page
        main_column = self.page.controls[0]
        if isinstance(main_column, ft.Column) and len(main_column.controls) >= 2:
            main_column.controls[-1] = new_nav
            self.nav_bar = new_nav

    def _update_theme_toggle_container(self):
        """Update theme toggle container after theme change."""
        # The container is transparent, so no update needed
        pass

    def _update_banner_image(self):
        """Update banner image colors for current theme."""
        if hasattr(self, "banner_image"):
            self.banner_image.color = ft.Colors.WHITE if self.is_dark_mode else None
            self.banner_image.color_blend_mode = ft.BlendMode.DIFFERENCE if self.is_dark_mode else None

    def _create_theme_toggle_button(self) -> ft.IconButton:
        """Create the sun/moon theme toggle button."""
        colors = self._get_colors()
        # Show sun icon in dark mode (to switch to light), moon in light mode (to switch to dark)
        icon = ft.Icons.LIGHT_MODE_OUTLINED if self.is_dark_mode else ft.Icons.DARK_MODE_OUTLINED
        tooltip = "Switch to light mode" if self.is_dark_mode else "Switch to dark mode"

        return ft.IconButton(
            icon=icon,
            icon_color=colors["foreground"],
            tooltip=tooltip,
            on_click=self._on_theme_icon_click,
        )

    def _update_theme_toggle_button(self):
        """Update the theme toggle button icon after theme change."""
        colors = self._get_colors()
        icon = ft.Icons.LIGHT_MODE_OUTLINED if self.is_dark_mode else ft.Icons.DARK_MODE_OUTLINED
        tooltip = "Switch to light mode" if self.is_dark_mode else "Switch to dark mode"

        self.theme_toggle_btn.icon = icon
        self.theme_toggle_btn.icon_color = colors["foreground"]
        self.theme_toggle_btn.tooltip = tooltip

    def _on_theme_icon_click(self, e):
        """Handle theme icon button click."""
        # Disable match system theme when manually toggling
        if self.match_system_theme:
            self.match_system_theme = False
            # Update the settings switch if it exists
            if hasattr(self, "system_theme_switch"):
                self.system_theme_switch.value = False

        # Toggle theme
        self.is_dark_mode = not self.is_dark_mode
        log_message(message_type="ui_theme_toggle", dark_mode=self.is_dark_mode, manual=True)

        # Apply new theme
        apply_theme_mode(self.page, self.is_dark_mode)
        self._save_theme_preference()

        # Update UI elements
        self._update_theme_toggle_button()
        self._update_theme_toggle_container()
        self._update_banner_image()
        self._rebuild_nav_bar()

        self.page.update()

    def _on_nav_change(self, index: int):
        """Handle navigation item click."""
        self.active_nav_index = index
        view_name = self.NAV_ITEMS[index]["view"]
        log_message(message_type="ui_nav_change", view=view_name)
        self._switch_view(view_name)
        self._rebuild_nav_bar()
        self.page.update()

    def _switch_view(self, view_name: str):
        """Switch to the specified view."""
        self.current_view = view_name
        for name, view in self.views.items():
            view.visible = name == view_name

        # Update header row visibility (theme toggle only on home page)
        self.header_row.visible = view_name == "home"

        # Refresh list view when switching to it
        if view_name == "list":
            self._refresh_list_view()

    def _get_colors(self):
        """Get current color palette based on theme."""
        return get_colors(self.is_dark_mode)

    # ===== HOME VIEW =====

    def _create_home_view(self) -> ft.Container:
        """Create the home view with roll lunch functionality."""
        colors = self._get_colors()

        # Banner image - responsive width, inverted for dark mode
        self.banner_image = ft.Image(
            src="logo.png",
            width=300,
            fit=ft.ImageFit.CONTAIN,
            color=ft.Colors.WHITE if self.is_dark_mode else None,
            color_blend_mode=ft.BlendMode.DIFFERENCE if self.is_dark_mode else None,
        )
        banner_container = ft.Container(
            content=self.banner_image,
            alignment=ft.alignment.center,
        )

        # Result text
        self.result_text = ft.Text(
            "",
            size=24,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        )

        # Category selector
        self.category_radio = ft.RadioGroup(
            content=ft.Row(
                [
                    ft.Radio(value="cheap", label="Cheap"),
                    ft.Radio(value="Normal", label="Normal"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=SPACING["lg"],
            ),
            value="Normal",
            on_change=self._on_category_changed,
        )

        # Roll button
        roll_button = ft.Container(
            content=ft.ElevatedButton(
                text="Roll Lunch",
                on_click=self._on_roll_lunch_clicked,
                style=ft.ButtonStyle(
                    color=colors["primary_foreground"],
                    bgcolor=colors["primary"],
                    padding=ft.padding.symmetric(horizontal=32, vertical=16),
                ),
            ),
            alignment=ft.alignment.center,
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(expand=True),  # Spacer
                    banner_container,
                    ft.Container(height=SPACING["lg"]),
                    self.category_radio,
                    ft.Container(height=SPACING["lg"]),
                    roll_button,
                    ft.Container(height=SPACING["xl"]),
                    self.result_text,
                    ft.Container(expand=True),  # Spacer
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
            ),
            expand=True,
            visible=True,
        )

    def _on_category_changed(self, e):
        """Handle category radio button change."""
        log_message(message_type="ui_radio_changed", option=e.control.value)

    def _on_roll_lunch_clicked(self, e):
        """Handle roll lunch button click."""
        category = self.category_radio.value
        log_message(message_type="ui_button_click", button="roll_lunch", option=category)
        if self.on_roll_lunch:
            try:
                result = self.on_roll_lunch(category)
                self.result_text.value = result
                self.page.update()
            except Exception as ex:
                self.result_text.value = str(ex)
                self.page.update()

    # ===== ADD VIEW =====

    def _create_add_view(self) -> ft.Container:
        """Create the add restaurant view."""
        colors = self._get_colors()

        # Warning text for similar names
        self.add_warning_text = ft.Text(
            "",
            color=colors["destructive"],
            visible=False,
        )

        # Feedback text
        self.add_feedback_text = ft.Text(
            "",
            text_align=ft.TextAlign.CENTER,
        )

        # Name input
        self.add_name_field = create_styled_textfield(
            "Restaurant Name",
            on_change=self._on_add_name_changed,
        )

        # Category selector
        self.add_category_radio = ft.RadioGroup(
            content=ft.Row(
                [
                    ft.Radio(value="cheap", label="Cheap"),
                    ft.Radio(value="Normal", label="Normal"),
                ],
                spacing=SPACING["lg"],
            ),
            value="Normal",
        )

        # Add button
        add_button = ft.ElevatedButton(
            text="Add Restaurant",
            on_click=self._on_add_restaurant_clicked,
            style=ft.ButtonStyle(
                color=colors["primary_foreground"],
                bgcolor=colors["primary"],
            ),
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Add Restaurant",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(height=SPACING["lg"]),
                    self.add_name_field,
                    self.add_warning_text,
                    ft.Container(height=SPACING["md"]),
                    ft.Text("Category:"),
                    self.add_category_radio,
                    ft.Container(height=SPACING["lg"]),
                    add_button,
                    ft.Container(height=SPACING["md"]),
                    self.add_feedback_text,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.START,
                scroll=ft.ScrollMode.AUTO,
            ),
            expand=True,
            visible=False,
        )

    def _on_add_name_changed(self, e):
        """Check for similar names as user types."""
        name = e.control.value
        if not name:
            self.add_warning_text.visible = False
            self.page.update()
            return

        # Get existing restaurants
        existing = []
        if self.on_get_all_restaurants:
            with contextlib.suppress(Exception):
                existing = self.on_get_all_restaurants()

        # Check for similar names
        normalized_input = normalize_name(name)
        similar = []
        for restaurant_name, _ in existing:
            if normalize_name(restaurant_name) == normalized_input and restaurant_name != name:
                similar.append(restaurant_name)

        if similar:
            self.add_warning_text.value = f"Similar name exists: {', '.join(similar)}"
            self.add_warning_text.visible = True
        else:
            self.add_warning_text.visible = False
        self.page.update()

    def _on_add_restaurant_clicked(self, e):
        """Handle add restaurant button click."""
        name = self.add_name_field.value
        if not name:
            self.add_feedback_text.value = "Please enter a restaurant name"
            self.page.update()
            return

        category = self.add_category_radio.value
        log_message(message_type="ui_button_click", button="add_restaurant", name=name, category=category)

        if self.on_add_restaurant:
            try:
                result = self.on_add_restaurant(name, category)
                self.add_feedback_text.value = result
                self.add_name_field.value = ""
                self.add_warning_text.visible = False
                self.page.update()
            except Exception as ex:
                self.add_feedback_text.value = str(ex)
                self.page.update()

    # ===== LIST VIEW =====

    def _create_list_view(self) -> ft.Container:
        """Create the list view showing all restaurants."""
        # List container
        self.restaurant_list = ft.ListView(
            controls=[],
            spacing=SPACING["sm"],
            padding=SPACING["sm"],
            expand=True,
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "All Restaurants",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(height=SPACING["md"]),
                    ft.Container(
                        content=self.restaurant_list,
                        expand=True,
                        border=ft.border.all(1, self._get_colors()["border"]),
                        border_radius=BORDER_RADIUS["md"],
                    ),
                ],
                expand=True,
            ),
            expand=True,
            visible=False,
        )

    def _refresh_list_view(self):
        """Refresh the restaurant list."""
        if not self.on_get_all_restaurants:
            return

        try:
            restaurants = self.on_get_all_restaurants()
        except Exception as ex:
            self.restaurant_list.controls = [ft.Text(f"Error: {ex}")]
            return

        colors = self._get_colors()

        # Create list items with delete buttons
        items = []
        for name, category in restaurants:
            items.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(f"{name}", expand=True),
                            ft.Text(f"({category})", color=colors["muted_foreground"]),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color=colors["destructive"],
                                tooltip="Delete",
                                on_click=lambda e, n=name: self._on_delete_restaurant(n),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=ft.padding.symmetric(horizontal=SPACING["md"], vertical=SPACING["sm"]),
                    border=ft.border.only(bottom=ft.BorderSide(1, colors["border"])),
                )
            )

        self.restaurant_list.controls = items

    def _on_delete_restaurant(self, name: str):
        """Handle delete restaurant click."""
        log_message(message_type="ui_button_click", button="delete_restaurant", name=name)
        if self.on_delete_restaurant:
            try:
                result = self.on_delete_restaurant(name)
                self._refresh_list_view()
                self.page.update()
            except Exception as ex:
                pass

    # ===== SETTINGS VIEW =====

    def _create_settings_view(self) -> ft.Container:
        """Create the settings view with system theme toggle."""
        colors = self._get_colors()

        # Match system theme toggle
        self.system_theme_switch = ft.Switch(
            label="Match system theme",
            value=self.match_system_theme,
            on_change=self._on_system_theme_toggle,
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Settings",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(height=SPACING["lg"]),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.BRIGHTNESS_AUTO, color=colors["foreground"]),
                                        ft.Container(width=SPACING["md"]),
                                        self.system_theme_switch,
                                    ],
                                ),
                                ft.Text(
                                    "When enabled, follows your device's appearance setting. "
                                    "When disabled, use the icon in the top-right to toggle manually.",
                                    size=12,
                                    color=colors["muted_foreground"],
                                ),
                            ],
                            spacing=SPACING["sm"],
                        ),
                        padding=SPACING["md"],
                        border=ft.border.all(1, colors["border"]),
                        border_radius=BORDER_RADIUS["md"],
                    ),
                    ft.Container(height=SPACING["xl"]),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text("About", weight=ft.FontWeight.BOLD),
                                ft.Text("Lunch - Restaurant Selector"),
                                ft.Text("Version 1.0.0", color=colors["muted_foreground"]),
                            ],
                            spacing=SPACING["sm"],
                        ),
                        padding=SPACING["md"],
                        border=ft.border.all(1, colors["border"]),
                        border_radius=BORDER_RADIUS["md"],
                    ),
                ],
            ),
            expand=True,
            visible=False,
        )

    def _on_system_theme_toggle(self, e):
        """Handle match system theme toggle switch."""
        self.match_system_theme = e.control.value
        log_message(message_type="ui_system_theme_toggle", match_system=self.match_system_theme)

        if self.match_system_theme:
            # Switch to system theme
            self.is_dark_mode = self._detect_system_theme()
            apply_theme_mode(self.page, self.is_dark_mode)
            self._update_theme_toggle_button()
            self._update_theme_toggle_container()
            self._update_banner_image()
            self._rebuild_nav_bar()

        self._save_theme_preference()
        self.page.update()

    # ===== PUBLIC INTERFACE =====

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


def create_gui(page: ft.Page) -> LunchGUI:
    """Factory function to create and return a LunchGUI instance."""
    return LunchGUI(page)
