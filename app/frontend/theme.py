"""
Basecoat UI design system implementation for Flet.
This module provides design tokens and theme configuration following Basecoat conventions.
"""

import flet as ft
from typing import Any, TypedDict


class ColorPalette(TypedDict):
    """Basecoat semantic color palette."""

    primary: str
    primary_foreground: str
    secondary: str
    secondary_foreground: str
    muted: str
    muted_foreground: str
    accent: str
    accent_foreground: str
    destructive: str
    destructive_foreground: str
    background: str
    foreground: str
    card: str
    card_foreground: str
    border: str
    input: str
    ring: str


class TypographyScale(TypedDict):
    """Typography configuration."""

    size: int
    weight: str


class SpacingTokens(TypedDict):
    """Spacing values in pixels."""

    xs: int
    sm: int
    md: int
    lg: int
    xl: int


class BorderRadiusTokens(TypedDict):
    """Border radius values in pixels."""

    sm: int
    md: int
    lg: int
    full: int


# Light theme colors (Basecoat UI with Zinc palette)
LIGHT_COLORS: ColorPalette = {
    "primary": "#18181b",  # zinc-900
    "primary_foreground": "#fafafa",
    "secondary": "#f4f4f5",  # zinc-100
    "secondary_foreground": "#18181b",
    "muted": "#f4f4f5",
    "muted_foreground": "#71717a",
    "accent": "#f4f4f5",
    "accent_foreground": "#18181b",
    "destructive": "#ef4444",  # red-500
    "destructive_foreground": "#fafafa",
    "background": "#ffffff",
    "foreground": "#09090b",
    "card": "#ffffff",
    "card_foreground": "#09090b",
    "border": "#e4e4e7",  # zinc-200
    "input": "#e4e4e7",
    "ring": "#18181b",
}

# Dark theme colors (Basecoat UI with Zinc palette)
DARK_COLORS: ColorPalette = {
    "primary": "#fafafa",
    "primary_foreground": "#18181b",
    "secondary": "#27272a",  # zinc-800
    "secondary_foreground": "#fafafa",
    "muted": "#27272a",
    "muted_foreground": "#a1a1aa",
    "accent": "#27272a",
    "accent_foreground": "#fafafa",
    "destructive": "#dc2626",  # red-600
    "destructive_foreground": "#fafafa",
    "background": "#09090b",
    "foreground": "#fafafa",
    "card": "#09090b",
    "card_foreground": "#fafafa",
    "border": "#27272a",
    "input": "#27272a",
    "ring": "#d4d4d8",
}

# Spacing tokens (in pixels)
SPACING: SpacingTokens = {
    "xs": 4,  # gap-1
    "sm": 8,  # gap-2
    "md": 16,  # gap-4
    "lg": 24,  # gap-6
    "xl": 32,  # gap-8
}

# Border radius tokens (in pixels) - flat design
BORDER_RADIUS: BorderRadiusTokens = {
    "sm": 2,
    "md": 4,
    "lg": 6,
    "full": 9999,  # pill shape
}

# Navigation bar constants
NAV_BAR_HEIGHT = 64

# Typography tokens
TYPOGRAPHY: dict[str, TypographyScale] = {
    "heading": {
        "size": 24,
        "weight": "bold",
    },
    "body": {
        "size": 14,
        "weight": "normal",
    },
    "label": {
        "size": 12,
        "weight": "w500",
    },
}


class BasecoatTheme:
    """Basecoat design token definitions and theme factory."""

    # Expose design tokens as class attributes
    COLORS = {"light": LIGHT_COLORS, "dark": DARK_COLORS}
    TYPOGRAPHY = TYPOGRAPHY
    SPACING = SPACING
    BORDER_RADIUS = BORDER_RADIUS

    @staticmethod
    def create_light_theme() -> ft.Theme:
        """Create Flet theme with Basecoat light color palette."""
        colors = LIGHT_COLORS

        return ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=colors["primary"],
                on_primary=colors["primary_foreground"],
                secondary=colors["secondary"],
                on_secondary=colors["secondary_foreground"],
                background=colors["background"],
                on_background=colors["foreground"],
                surface=colors["card"],
                on_surface=colors["card_foreground"],
                error=colors["destructive"],
                on_error=colors["destructive_foreground"],
                outline=colors["border"],
                surface_variant=colors["muted"],
                on_surface_variant=colors["muted_foreground"],
            )
        )

    @staticmethod
    def create_dark_theme() -> ft.Theme:
        """Create Flet theme with Basecoat dark color palette."""
        colors = DARK_COLORS

        return ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=colors["primary"],
                on_primary=colors["primary_foreground"],
                secondary=colors["secondary"],
                on_secondary=colors["secondary_foreground"],
                background=colors["background"],
                on_background=colors["foreground"],
                surface=colors["card"],
                on_surface=colors["card_foreground"],
                error=colors["destructive"],
                on_error=colors["destructive_foreground"],
                outline=colors["border"],
                surface_variant=colors["muted"],
                on_surface_variant=colors["muted_foreground"],
            )
        )

    @staticmethod
    def apply_theme(page: ft.Page) -> None:
        """Apply Basecoat theme to a Flet page with system theme detection."""
        # Detect system theme preference
        # Flet's page.platform_brightness returns "dark" or "light"
        is_dark_mode = page.platform_brightness == ft.Brightness.DARK if page.platform_brightness else False

        # Apply appropriate theme
        if is_dark_mode:
            page.theme = BasecoatTheme.create_dark_theme()
            page.theme_mode = ft.ThemeMode.DARK
        else:
            page.theme = BasecoatTheme.create_light_theme()
            page.theme_mode = ft.ThemeMode.LIGHT

        # Set up theme change listener for runtime switching
        def on_theme_change(e):
            """Handle system theme changes at runtime."""
            if page.platform_brightness == ft.Brightness.DARK:
                page.theme = BasecoatTheme.create_dark_theme()
                page.theme_mode = ft.ThemeMode.DARK
            else:
                page.theme = BasecoatTheme.create_light_theme()
                page.theme_mode = ft.ThemeMode.LIGHT
            page.update()

        # Note: Flet doesn't have a direct event for platform_brightness changes
        # The theme will be applied on page load based on system preference
        # For manual theme switching, the application can call apply_theme again

        page.update()


# Component Factory Functions


def create_primary_button(text: str, on_click: Any) -> ft.ElevatedButton:
    """
    Create a Basecoat-styled primary button with filled background.

    Args:
        text: Button label text
        on_click: Click event handler

    Returns:
        ElevatedButton with primary styling
    """
    return ft.ElevatedButton(
        text=text,
        on_click=on_click,
        style=ft.ButtonStyle(
            color=LIGHT_COLORS["primary_foreground"],  # Text color
            bgcolor=LIGHT_COLORS["primary"],  # Background color
        ),
    )


def create_outline_button(text: str, on_click: Any) -> ft.OutlinedButton:
    """
    Create a Basecoat-styled outline button with border styling.

    Args:
        text: Button label text
        on_click: Click event handler

    Returns:
        OutlinedButton with outline styling
    """
    return ft.OutlinedButton(
        text=text,
        on_click=on_click,
        style=ft.ButtonStyle(
            color=LIGHT_COLORS["foreground"],  # Text color
            side=ft.BorderSide(
                width=1,
                color=LIGHT_COLORS["border"],
            ),
        ),
    )


def create_destructive_button(text: str, on_click: Any) -> ft.ElevatedButton:
    """
    Create a Basecoat-styled destructive button with destructive colors.

    Args:
        text: Button label text
        on_click: Click event handler

    Returns:
        ElevatedButton with destructive styling
    """
    return ft.ElevatedButton(
        text=text,
        on_click=on_click,
        style=ft.ButtonStyle(
            color=LIGHT_COLORS["destructive_foreground"],  # Text color
            bgcolor=LIGHT_COLORS["destructive"],  # Background color
        ),
    )


def create_card_container(content: ft.Control, **kwargs) -> ft.Container:
    """
    Create a Basecoat-styled card container with padding and border radius.

    Args:
        content: The control to wrap in the card container
        **kwargs: Additional Container properties to override defaults

    Returns:
        Container with card styling
    """
    # Default card styling
    defaults = {
        "content": content,
        "padding": SPACING["md"],
        "border_radius": BORDER_RADIUS["md"],
        "bgcolor": LIGHT_COLORS["card"],
        "border": ft.border.all(1, LIGHT_COLORS["border"]),
    }

    # Merge with any provided kwargs (kwargs take precedence)
    defaults.update(kwargs)

    return ft.Container(**defaults)


def create_modal_content(title: str, body: list[ft.Control], actions: list[ft.Control]) -> ft.Container:
    """
    Create a Basecoat-styled modal dialog content structure.

    Args:
        title: Modal title text
        body: List of controls for the modal body
        actions: List of button controls for the modal footer

    Returns:
        Container with modal card structure
    """
    return ft.Container(
        content=ft.Column(
            controls=[
                # Header section
                ft.Container(
                    content=ft.Text(
                        title,
                        size=TYPOGRAPHY["heading"]["size"],
                        weight=ft.FontWeight.BOLD,
                    ),
                    padding=ft.padding.only(
                        left=SPACING["lg"],
                        right=SPACING["lg"],
                        top=SPACING["lg"],
                        bottom=SPACING["md"],
                    ),
                ),
                # Body section
                ft.Container(
                    content=ft.Column(
                        controls=body,
                        spacing=SPACING["sm"],
                    ),
                    padding=ft.padding.only(
                        left=SPACING["lg"],
                        right=SPACING["lg"],
                        bottom=SPACING["md"],
                    ),
                ),
                # Footer section with actions
                ft.Container(
                    content=ft.Row(
                        controls=actions,
                        spacing=SPACING["sm"],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    padding=ft.padding.only(
                        left=SPACING["lg"],
                        right=SPACING["lg"],
                        bottom=SPACING["lg"],
                    ),
                ),
            ],
            spacing=0,
            tight=True,
        ),
        bgcolor=LIGHT_COLORS["card"],
        border_radius=BORDER_RADIUS["lg"],
        border=ft.border.all(1, LIGHT_COLORS["border"]),
    )


def create_styled_textfield(label: str, **kwargs) -> ft.TextField:
    """
    Create a Basecoat-styled text field with border color from tokens.

    Args:
        label: Label text for the text field
        **kwargs: Additional TextField properties to override defaults

    Returns:
        TextField with Basecoat styling
    """
    # Default text field styling
    defaults = {
        "label": label,
        "border_color": LIGHT_COLORS["input"],
        "focused_border_color": LIGHT_COLORS["ring"],
        "bgcolor": LIGHT_COLORS["background"],
        "color": LIGHT_COLORS["foreground"],
        "border_radius": BORDER_RADIUS["sm"],
    }

    # Merge with any provided kwargs (kwargs take precedence)
    defaults.update(kwargs)

    return ft.TextField(**defaults)


def get_colors(is_dark: bool) -> ColorPalette:
    """Get the color palette for the specified theme mode."""
    return DARK_COLORS if is_dark else LIGHT_COLORS


def apply_theme_mode(page: ft.Page, is_dark: bool) -> None:
    """Apply theme mode manually (for toggle switch)."""
    if is_dark:
        page.theme = BasecoatTheme.create_dark_theme()
        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor = DARK_COLORS["background"]
    else:
        page.theme = BasecoatTheme.create_light_theme()
        page.theme_mode = ft.ThemeMode.LIGHT
        page.bgcolor = LIGHT_COLORS["background"]
    page.update()


def create_nav_item(
    icon: str,
    label: str,
    is_active: bool,
    on_click: Any,
    is_dark: bool = False,
) -> ft.Container:
    """
    Create a navigation bar item with icon and label.

    Args:
        icon: Flet icon name
        label: Text label below icon
        is_active: Whether this item is currently active
        on_click: Click event handler
        is_dark: Whether dark mode is active

    Returns:
        Container with nav item styling
    """
    colors = get_colors(is_dark)
    active_color = colors["primary"]
    inactive_color = colors["muted_foreground"]
    current_color = active_color if is_active else inactive_color

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(icon, color=current_color, size=24),
                ft.Text(label, size=10, color=current_color, weight=ft.FontWeight.W_500 if is_active else None),
            ],
            spacing=2,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        expand=True,
        padding=ft.padding.symmetric(vertical=8),
        on_click=on_click,
        ink=True,
    )


def create_nav_bar(
    items: list[dict],
    active_index: int,
    on_change: Any,
    is_dark: bool = False,
) -> ft.Container:
    """
    Create a bottom navigation bar.

    Args:
        items: List of dicts with 'icon' and 'label' keys
        active_index: Index of currently active item
        on_change: Callback function(index) when item is clicked
        is_dark: Whether dark mode is active

    Returns:
        Container with navigation bar
    """
    colors = get_colors(is_dark)

    nav_items = []
    for i, item in enumerate(items):
        nav_items.append(
            create_nav_item(
                icon=item["icon"],
                label=item["label"],
                is_active=(i == active_index),
                on_click=lambda e, idx=i: on_change(idx),
                is_dark=is_dark,
            )
        )

    return ft.Container(
        content=ft.Row(
            controls=nav_items,
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
        ),
        height=NAV_BAR_HEIGHT,
        bgcolor=colors["card"],
        border=ft.border.only(top=ft.BorderSide(1, colors["border"])),
    )
