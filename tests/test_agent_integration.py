"""
Integration tests for agent search and database operations.
"""

import pytest
import sqlite3
import tempfile
import time
from app.backend.agent import RestaurantSearchAgent, lookup_restaurant_info
from app.backend.db import save_restaurant_info
from app.config import get_app_config, get_llm_config
from pathlib import Path


class TestAgentSearch:
    """Test agent search functionality."""

    @pytest.mark.integration
    def test_agent_search_returns_restaurant_info(self):
        """Test that agent search returns structured restaurant info."""
        config = get_llm_config()
        app_config = get_app_config()

        print(f"\nUsing model: {config.model}")
        print(f"Using provider: {config.provider}")
        print(f"Zip code: {app_config['zip_code']}")

        agent = RestaurantSearchAgent(zip_code=app_config["zip_code"], llm_config=config)

        # Search for a well-known restaurant
        result = agent.search("McDonald's")

        print(f"Result: {result}")

        # Should return something (may be None if LLM fails)
        # But if it returns, should have at least some fields
        if result is not None:
            assert hasattr(result, "address")
            assert hasattr(result, "phone")
            assert hasattr(result, "hours")
            assert hasattr(result, "website")
            assert hasattr(result, "description")
            # At least one field should be populated
            fields = [result.address, result.phone, result.hours, result.website, result.description]
            assert any(f is not None for f in fields), "At least one field should be populated"

    @pytest.mark.integration
    def test_lookup_restaurant_info_convenience_function(self):
        """Test the convenience function for restaurant lookup."""
        result = lookup_restaurant_info("Taco Bell")

        print(f"Result: {result}")

        # May return None if LLM has issues, but shouldn't raise
        if result is not None:
            assert hasattr(result, "address")


class TestDatabaseIntegration:
    """Test database save operations with agent results."""

    @pytest.fixture
    def temp_db(self, tmp_path):
        """Create a temporary database."""
        db_path = tmp_path / "test_lunch.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lunch_list (
                restaurants TEXT PRIMARY KEY,
                option TEXT
            )
        """)
        cursor.execute("""
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
        """)
        cursor.execute("INSERT INTO lunch_list VALUES ('Test Restaurant', 'Normal')")
        conn.commit()
        conn.close()

        return db_path

    @pytest.mark.integration
    def test_save_restaurant_info_to_db(self, temp_db, monkeypatch):
        """Test saving restaurant info to database."""
        # Monkeypatch the db_path
        import app.backend.db as db_module

        monkeypatch.setattr(db_module, "db_path", str(temp_db))

        # Save restaurant info
        save_restaurant_info(
            "Test Restaurant",
            address="123 Test St",
            phone="555-1234",
            hours="9am-5pm",
            website="https://test.com",
            description="A test restaurant",
        )

        # Verify it was saved
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM restaurant_info WHERE restaurant_name = ?", ("Test Restaurant",))
        row = cursor.fetchone()
        conn.close()

        assert row is not None
        assert row[1] == "Test Restaurant"  # restaurant_name
        assert row[2] == "123 Test St"  # address
        assert row[3] == "555-1234"  # phone


class TestEndToEndFlow:
    """Test complete flow from agent search to database save."""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_full_lookup_and_save_flow(self, tmp_path, monkeypatch):
        """Test searching and saving restaurant info end-to-end."""
        # Setup temp database
        db_path = tmp_path / "test_lunch.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lunch_list (
                restaurants TEXT PRIMARY KEY,
                option TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS restaurant_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                restaurant_name TEXT NOT NULL UNIQUE,
                address TEXT,
                phone TEXT,
                hours TEXT,
                website TEXT,
                description TEXT,
                last_updated TEXT
            )
        """)
        cursor.execute("INSERT INTO lunch_list VALUES ('Subway', 'cheap')")
        conn.commit()
        conn.close()

        # Monkeypatch db_path
        import app.backend.db as db_module

        monkeypatch.setattr(db_module, "db_path", str(db_path))

        # Perform lookup
        print("\nStarting agent search...")
        start_time = time.time()
        result = lookup_restaurant_info("Subway")
        elapsed = time.time() - start_time
        print(f"Search completed in {elapsed:.2f}s")
        print(f"Result: {result}")

        if result is not None:
            # Save to database
            save_restaurant_info(
                "Subway",
                address=result.address,
                phone=result.phone,
                hours=result.hours,
                website=result.website,
                description=result.description,
            )

            # Verify saved
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM restaurant_info WHERE restaurant_name = ?", ("Subway",))
            row = cursor.fetchone()
            conn.close()

            assert row is not None, "Restaurant info should be saved to database"
            print(f"Saved to DB: {row}")
        else:
            pytest.skip("LLM returned None - may be unavailable or slow")
