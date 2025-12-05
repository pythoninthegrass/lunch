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
    "primary": "#18181b",        # zinc-900
    "primary_foreground": "#fafafa",
    "secondary": "#f4f4f5",      # zinc-100
    "secondary_foreground": "#18181b",
    "muted": "#f4f4f5",
    "muted_foreground": "#71717a",
    "accent": "#f4f4f5",
    "accent_foreground": "#18181b",
    "destructive": "#ef4444",    # red-500
    "destructive_foreground": "#fafafa",
    "background": "#ffffff",
    "foreground": "#09090b",
    "card": "#ffffff",
    "card_foreground": "#09090b",
    "border": "#e4e4e7",         # zinc-200
    "input": "#e4e4e7",
    "ring": "#18181b",
}

# Dark theme colors (Basecoat UI with Zinc palette)
DARK_COLORS: ColorPalette = {
    "primary": "#fafafa",
    "primary_foreground": "#18181b",
    "secondary": "#27272a",      # zinc-800
    "secondary_foreground": "#fafafa",
    "muted": "#27272a",
    "muted_foreground": "#a1a1aa",
    "accent": "#27272a",
    "accent_foreground": "#fafafa",
    "destructive": "#dc2626",    # red-600
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
    "xs": 4,   # gap-1
    "sm": 8,   # gap-2
    "md": 16,  # gap-4
    "lg": 24,  # gap-6
    "xl": 32,  # gap-8
}

# Border radius tokens (in pixels)
BORDER_RADIUS: BorderRadiusTokens = {
    "sm": 4,
    "md": 8,
    "lg": 12,
    "full": 9999,  # pill shape
}

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
