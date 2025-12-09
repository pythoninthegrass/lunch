"""
Tests for FastHTML web application routes.
Tests HTTP endpoints and HTMX partial responses.
"""

import pytest
import sqlite3
import tempfile
from starlette.testclient import TestClient
from unittest.mock import patch
from urllib.parse import quote


@pytest.fixture
def test_db_path():
    """Create a temporary database with sample data."""
    temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_db_path = temp_file.name
    temp_file.close()

    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()

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

    yield temp_db_path

    import os
    if os.path.exists(temp_db_path):
        os.unlink(temp_db_path)


@pytest.fixture
def client(test_db_path):
    """Create test client with patched database."""
    with patch('app.backend.db.db_path', test_db_path):
        from app.main import application
        with TestClient(application) as client:
            yield client


class TestHomeRoute:
    """Tests for the home page route."""

    def test_home_returns_200(self, client):
        """Home page should return 200 status."""
        response = client.get("/")
        assert response.status_code == 200

    def test_home_contains_roll_button(self, client):
        """Home page should contain Roll Lunch button."""
        response = client.get("/")
        assert b"Roll Lunch" in response.content

    def test_home_contains_radio_options(self, client):
        """Home page should contain cheap and normal radio options."""
        response = client.get("/")
        content = response.content.decode()
        assert 'value="cheap"' in content
        assert 'value="normal"' in content

    def test_home_contains_logo(self, client):
        """Home page should contain logo image."""
        response = client.get("/")
        assert b'src="logo.png"' in response.content


class TestRollRoute:
    """Tests for the roll lunch endpoint."""

    def test_roll_normal_returns_restaurant(self, client):
        """Rolling normal should return a restaurant name."""
        response = client.post("/roll", data={"option": "normal"})
        assert response.status_code == 200
        content = response.content.decode()
        # Should return one of the Normal restaurants
        assert any(name in content for name in ["The Ritz", "Fine Dining", "Steakhouse"])

    def test_roll_cheap_returns_restaurant(self, client):
        """Rolling cheap should return a cheap restaurant name."""
        response = client.post("/roll", data={"option": "cheap"})
        assert response.status_code == 200
        content = response.content.decode()
        # Should return one of the cheap restaurants
        assert any(name in content for name in ["McDonald's", "Burger King", "Subway"])

    def test_roll_empty_category_returns_error(self, test_db_path):
        """Rolling from empty category should show error message."""
        # Create empty database
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM lunch_list WHERE option = 'cheap'")
        conn.commit()
        conn.close()

        with patch('app.backend.db.db_path', test_db_path):
            from app.main import application
            with TestClient(application) as client:
                response = client.post("/roll", data={"option": "cheap"})
                assert response.status_code == 200
                assert b"No restaurants found" in response.content


class TestAddRoute:
    """Tests for the add restaurant routes."""

    def test_add_page_returns_200(self, client):
        """Add page should return 200 status."""
        response = client.get("/add")
        assert response.status_code == 200

    def test_add_page_contains_form(self, client):
        """Add page should contain form with required fields."""
        response = client.get("/add")
        content = response.content.decode()
        assert 'name="name"' in content
        assert 'name="option"' in content
        assert "Add Restaurant" in content

    def test_add_restaurant_success(self, client, test_db_path):
        """Adding a new restaurant should succeed."""
        response = client.post("/add", data={
            "name": "New Test Restaurant",
            "option": "normal"
        })
        assert response.status_code == 200
        assert b"Added restaurant: New Test Restaurant" in response.content

        # Verify in database
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM lunch_list WHERE restaurants = ?", ("New Test Restaurant",))
        result = cursor.fetchone()
        conn.close()
        assert result is not None
        assert result[0] == "New Test Restaurant"

    def test_add_duplicate_restaurant_fails(self, client):
        """Adding a duplicate restaurant should show error."""
        response = client.post("/add", data={
            "name": "McDonald's",
            "option": "cheap"
        })
        assert response.status_code == 200
        assert b"already exists" in response.content


class TestListRoute:
    """Tests for the list restaurants route."""

    def test_list_returns_200(self, client):
        """List page should return 200 status."""
        response = client.get("/list")
        assert response.status_code == 200

    def test_list_contains_restaurants(self, client):
        """List page should display all restaurants."""
        response = client.get("/list")
        content = response.content.decode()
        assert "McDonald's" in content
        assert "The Ritz" in content

    def test_list_shows_price_indicators(self, client):
        """List page should show price indicators."""
        response = client.get("/list")
        content = response.content.decode()
        # $ for cheap, $$ for normal
        assert "$" in content


class TestDeleteRoute:
    """Tests for the delete restaurant endpoint."""

    def test_delete_restaurant_success(self, client, test_db_path):
        """Deleting a restaurant should remove it."""
        # Use a restaurant without apostrophe for simpler test
        response = client.post(f"/delete?name={quote('Subway')}")
        assert response.status_code == 200
        # Response contains updated list view - Subway should not be in restaurant cards
        # Note: "Subway" may appear in URL but not in restaurant-card spans
        assert b'<span class="flex-1">Subway</span>' not in response.content

        # Verify in database
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM lunch_list WHERE restaurants = ?", ("Subway",))
        result = cursor.fetchone()
        conn.close()
        assert result is None

    def test_delete_nonexistent_silent(self, client):
        """Deleting nonexistent restaurant should not error."""
        response = client.post(f"/delete?name={quote('NonExistent')}")
        assert response.status_code == 200


class TestSettingsRoute:
    """Tests for the settings route."""

    def test_settings_returns_200(self, client):
        """Settings page should return 200 status."""
        response = client.get("/settings")
        assert response.status_code == 200

    def test_settings_contains_theme_toggle(self, client):
        """Settings page should contain theme toggle."""
        response = client.get("/settings")
        content = response.content.decode()
        assert "system-theme" in content
        assert "Match system theme" in content

    def test_settings_contains_about(self, client):
        """Settings page should contain about section."""
        response = client.get("/settings")
        assert b"About" in response.content
        assert b"Lunch - Restaurant Selector" in response.content


class TestNavigation:
    """Tests for navigation elements."""

    def test_all_pages_have_nav(self, client):
        """All pages should have bottom navigation."""
        for route in ["/", "/add", "/list", "/settings"]:
            response = client.get(route)
            assert b"bottom-nav" in response.content

    def test_nav_links_correct(self, client):
        """Navigation links should point to correct routes."""
        response = client.get("/")
        content = response.content.decode()
        assert 'href="/"' in content
        assert 'href="/add"' in content
        assert 'href="/list"' in content
        assert 'href="/settings"' in content

    def test_active_tab_highlighted(self, client):
        """Active tab should be marked."""
        response = client.get("/add")
        content = response.content.decode()
        # The add nav item should have active class
        assert 'class="nav-item active"' in content or "nav-item active" in content
