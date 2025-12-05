"""
Property-based and unit tests for the Basecoat theme module.

**Feature: basecoat-ui-refactor**
"""

import pytest
import re
from app.frontend.theme import (
    BORDER_RADIUS,
    DARK_COLORS,
    LIGHT_COLORS,
    SPACING,
    TYPOGRAPHY,
    BasecoatTheme,
    BorderRadiusTokens,
    ColorPalette,
    SpacingTokens,
    TypographyScale,
)
from hypothesis import given, strategies as st

# Property-Based Tests


@given(
    token_category=st.sampled_from(["colors_light", "colors_dark", "spacing", "border_radius", "typography"])
)
def test_design_token_completeness(token_category: str) -> None:
    """
    **Feature: basecoat-ui-refactor, Property 1: Design Token Completeness**
    **Validates: Requirements 1.1, 1.2, 1.3, 1.4**

    For any design token category (colors, typography, spacing, border radius),
    the theme module SHALL define all required keys with valid, non-empty values.
    """
    if token_category == "colors_light":
        # Test light color palette completeness
        palette = LIGHT_COLORS
        required_keys = ColorPalette.__annotations__.keys()

        # Check all required keys are present
        for key in required_keys:
            assert key in palette, f"Missing required color key: {key}"

            # Check value is non-empty string
            value = palette[key]
            assert isinstance(value, str), f"Color value for {key} must be a string"
            assert len(value) > 0, f"Color value for {key} must not be empty"

            # Check value is a valid hex color (basic validation)
            assert re.match(r"^#[0-9a-fA-F]{6}$", value), f"Color value for {key} must be a valid hex color: {value}"

    elif token_category == "colors_dark":
        # Test dark color palette completeness
        palette = DARK_COLORS
        required_keys = ColorPalette.__annotations__.keys()

        # Check all required keys are present
        for key in required_keys:
            assert key in palette, f"Missing required color key: {key}"

            # Check value is non-empty string
            value = palette[key]
            assert isinstance(value, str), f"Color value for {key} must be a string"
            assert len(value) > 0, f"Color value for {key} must not be empty"

            # Check value is a valid hex color (basic validation)
            assert re.match(r"^#[0-9a-fA-F]{6}$", value), f"Color value for {key} must be a valid hex color: {value}"

    elif token_category == "spacing":
        # Test spacing tokens completeness
        required_keys = SpacingTokens.__annotations__.keys()

        # Check all required keys are present
        for key in required_keys:
            assert key in SPACING, f"Missing required spacing key: {key}"

            # Check value is a positive integer
            value = SPACING[key]
            assert isinstance(value, int), f"Spacing value for {key} must be an integer"
            assert value > 0, f"Spacing value for {key} must be positive: {value}"

    elif token_category == "border_radius":
        # Test border radius tokens completeness
        required_keys = BorderRadiusTokens.__annotations__.keys()

        # Check all required keys are present
        for key in required_keys:
            assert key in BORDER_RADIUS, f"Missing required border_radius key: {key}"

            # Check value is a non-negative integer
            value = BORDER_RADIUS[key]
            assert isinstance(value, int), f"Border radius value for {key} must be an integer"
            assert value >= 0, f"Border radius value for {key} must be non-negative: {value}"

    elif token_category == "typography":
        # Test typography tokens completeness
        required_scales = ["heading", "body", "label"]

        # Check all required scales are present
        for scale in required_scales:
            assert scale in TYPOGRAPHY, f"Missing required typography scale: {scale}"

            # Check each scale has required properties
            scale_config = TYPOGRAPHY[scale]
            assert "size" in scale_config, f"Typography scale {scale} missing 'size' property"
            assert "weight" in scale_config, f"Typography scale {scale} missing 'weight' property"

            # Validate size is positive integer
            assert isinstance(scale_config["size"], int), f"Typography size for {scale} must be an integer"
            assert scale_config["size"] > 0, f"Typography size for {scale} must be positive: {scale_config['size']}"

            # Validate weight is non-empty string
            assert isinstance(scale_config["weight"], str), f"Typography weight for {scale} must be a string"
            assert len(scale_config["weight"]) > 0, f"Typography weight for {scale} must not be empty"


@given(theme_mode=st.sampled_from(["light", "dark"]))
def test_theme_mode_produces_valid_colors(theme_mode: str) -> None:
    """
    **Feature: basecoat-ui-refactor, Property 9: Theme Mode Produces Valid Colors**
    **Validates: Requirements 6.1, 6.2**

    For any theme mode (light or dark), the theme factory SHALL produce a theme
    with all required color values as valid hex color strings.
    """
    # Create the appropriate theme based on mode
    theme = BasecoatTheme.create_light_theme() if theme_mode == "light" else BasecoatTheme.create_dark_theme()

    # Verify theme object was created
    assert theme is not None, f"Theme factory for {theme_mode} mode returned None"
    assert hasattr(theme, "color_scheme"), f"Theme for {theme_mode} mode missing color_scheme attribute"

    # Get the color scheme
    color_scheme = theme.color_scheme
    assert color_scheme is not None, f"Color scheme for {theme_mode} mode is None"

    # Define all color properties that should be set in the color scheme
    color_properties = [
        "primary",
        "on_primary",
        "secondary",
        "on_secondary",
        "background",
        "on_background",
        "surface",
        "on_surface",
        "error",
        "on_error",
        "outline",
        "surface_variant",
        "on_surface_variant",
    ]

    # Hex color pattern (supports both #RRGGBB and #RRGGBBAA formats)
    hex_color_pattern = re.compile(r"^#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?$")

    # Verify each color property
    for prop in color_properties:
        assert hasattr(color_scheme, prop), f"Color scheme for {theme_mode} mode missing property: {prop}"

        color_value = getattr(color_scheme, prop)
        assert color_value is not None, f"Color property {prop} in {theme_mode} mode is None"
        assert isinstance(color_value, str), f"Color property {prop} in {theme_mode} mode must be a string, got {type(color_value)}"
        assert len(color_value) > 0, f"Color property {prop} in {theme_mode} mode must not be empty"
        assert hex_color_pattern.match(color_value), f"Color property {prop} in {theme_mode} mode must be a valid hex color: {color_value}"


@given(semantic_color_name=st.sampled_from(list(ColorPalette.__annotations__.keys())))
def test_semantic_colors_resolve_in_both_themes(semantic_color_name: str) -> None:
    """
    **Feature: basecoat-ui-refactor, Property 10: Semantic Colors Resolve in Both Themes**
    **Validates: Requirements 6.3**

    For any semantic color name used in the application, both the light and dark
    color palettes SHALL contain a valid color value for that name.
    """
    # Hex color pattern (supports #RRGGBB format)
    hex_color_pattern = re.compile(r"^#[0-9a-fA-F]{6}$")

    # Check that the semantic color exists in light theme
    assert semantic_color_name in LIGHT_COLORS, f"Semantic color '{semantic_color_name}' missing from LIGHT_COLORS"
    light_color_value = LIGHT_COLORS[semantic_color_name]

    # Validate light theme color value
    assert isinstance(light_color_value, str), f"Light theme color value for '{semantic_color_name}' must be a string"
    assert len(light_color_value) > 0, f"Light theme color value for '{semantic_color_name}' must not be empty"
    assert hex_color_pattern.match(light_color_value), f"Light theme color value for '{semantic_color_name}' must be a valid hex color: {light_color_value}"

    # Check that the semantic color exists in dark theme
    assert semantic_color_name in DARK_COLORS, f"Semantic color '{semantic_color_name}' missing from DARK_COLORS"
    dark_color_value = DARK_COLORS[semantic_color_name]

    # Validate dark theme color value
    assert isinstance(dark_color_value, str), f"Dark theme color value for '{semantic_color_name}' must be a string"
    assert len(dark_color_value) > 0, f"Dark theme color value for '{semantic_color_name}' must not be empty"
    assert hex_color_pattern.match(dark_color_value), f"Dark theme color value for '{semantic_color_name}' must be a valid hex color: {dark_color_value}"


# Unit Tests


def test_light_colors_has_all_required_keys() -> None:
    """Unit test: Verify light color palette has all required keys."""
    required_keys = ColorPalette.__annotations__.keys()
    for key in required_keys:
        assert key in LIGHT_COLORS, f"LIGHT_COLORS missing required key: {key}"


def test_dark_colors_has_all_required_keys() -> None:
    """Unit test: Verify dark color palette has all required keys."""
    required_keys = ColorPalette.__annotations__.keys()
    for key in required_keys:
        assert key in DARK_COLORS, f"DARK_COLORS missing required key: {key}"


def test_spacing_has_all_required_keys() -> None:
    """Unit test: Verify spacing tokens have all required keys."""
    required_keys = SpacingTokens.__annotations__.keys()
    for key in required_keys:
        assert key in SPACING, f"SPACING missing required key: {key}"


def test_border_radius_has_all_required_keys() -> None:
    """Unit test: Verify border radius tokens have all required keys."""
    required_keys = BorderRadiusTokens.__annotations__.keys()
    for key in required_keys:
        assert key in BORDER_RADIUS, f"BORDER_RADIUS missing required key: {key}"


def test_typography_has_all_required_scales() -> None:
    """Unit test: Verify typography has all required scales."""
    required_scales = ["heading", "body", "label"]
    for scale in required_scales:
        assert scale in TYPOGRAPHY, f"TYPOGRAPHY missing required scale: {scale}"


def test_basecoat_theme_exposes_design_tokens() -> None:
    """Unit test: Verify BasecoatTheme class exposes all design tokens."""
    assert hasattr(BasecoatTheme, "COLORS"), "BasecoatTheme missing COLORS attribute"
    assert hasattr(BasecoatTheme, "TYPOGRAPHY"), "BasecoatTheme missing TYPOGRAPHY attribute"
    assert hasattr(BasecoatTheme, "SPACING"), "BasecoatTheme missing SPACING attribute"
    assert hasattr(BasecoatTheme, "BORDER_RADIUS"), "BasecoatTheme missing BORDER_RADIUS attribute"

    # Verify COLORS contains both light and dark
    assert "light" in BasecoatTheme.COLORS, "BasecoatTheme.COLORS missing 'light' theme"
    assert "dark" in BasecoatTheme.COLORS, "BasecoatTheme.COLORS missing 'dark' theme"
