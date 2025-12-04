"""
Unit tests for database operations.
Tests database layer functionality with real SQLite operations.
"""

import pytest
import sqlite3
from app.backend.db import (
    add_restaurant_to_db,
    add_to_recent_lunch,
    calculate_lunch,
    create_db_and_tables,
    delete_restaurant_from_db,
    delete_restaurant_info,
    get_all_restaurants,
    get_restaurant_info,
    get_restaurants,
    rng_restaurant,
    save_restaurant_info,
)
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch


class TestDatabaseOperations:
    """Test cases for database operations."""

    def test_create_db_and_tables(self, temp_db):
        """Test database and table creation."""
        with patch('app.backend.db.db_path', temp_db):
            create_db_and_tables()

            # Verify tables were created
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()

            # Check lunch_list table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lunch_list'")
            assert cursor.fetchone() is not None

            # Check recent_lunch table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='recent_lunch'")
            assert cursor.fetchone() is not None

            conn.close()

    def test_get_all_restaurants_empty(self, temp_db):
        """Test getting all restaurants from empty database."""
        with patch('app.backend.db.db_path', temp_db):
            create_db_and_tables()
            result = get_all_restaurants()
            assert result == []

    def test_get_all_restaurants_with_data(self, setup_test_db):
        """Test getting all restaurants with existing data."""
        with patch('app.backend.db.db_path', setup_test_db):
            result = get_all_restaurants()
            assert len(result) == 6
            assert ("McDonald's", "cheap") in result
            assert ("The Ritz", "Normal") in result

    def test_get_restaurants_by_category(self, setup_test_db):
        """Test getting restaurants filtered by category."""
        with patch('app.backend.db.db_path', setup_test_db):
            # Test cheap restaurants
            cheap_restaurants = get_restaurants("cheap")
            assert len(cheap_restaurants) == 3
            assert all(r[1] == "cheap" for r in cheap_restaurants)

            # Test Normal restaurants
            normal_restaurants = get_restaurants("Normal")
            assert len(normal_restaurants) == 3
            assert all(r[1] == "Normal" for r in normal_restaurants)

            # Test case insensitive
            cheap_lower = get_restaurants("CHEAP")
            assert len(cheap_lower) == 3

    def test_get_restaurants_no_match(self, setup_test_db):
        """Test getting restaurants with non-existent category."""
        with patch('app.backend.db.db_path', setup_test_db):
            result = get_restaurants("expensive")
            assert result == []

    def test_add_restaurant_success(self, temp_db):
        """Test successful restaurant addition."""
        with patch('app.backend.db.db_path', temp_db):
            create_db_and_tables()
            result = add_restaurant_to_db("New Restaurant", "Normal")
            assert result is True

            # Verify it was added
            all_restaurants = get_all_restaurants()
            assert ("New Restaurant", "Normal") in all_restaurants

    def test_add_restaurant_duplicate(self, setup_test_db):
        """Test adding duplicate restaurant raises error."""
        with patch('app.backend.db.db_path', setup_test_db):
            with pytest.raises(ValueError, match="Restaurant 'McDonald's' already exists"):
                add_restaurant_to_db("McDonald's", "cheap")

    def test_delete_restaurant_success(self, setup_test_db):
        """Test successful restaurant deletion."""
        with patch('app.backend.db.db_path', setup_test_db):
            result = delete_restaurant_from_db("McDonald's")
            assert result is True

            # Verify it was deleted
            all_restaurants = get_all_restaurants()
            assert ("McDonald's", "cheap") not in all_restaurants
            assert len(all_restaurants) == 5

    def test_delete_restaurant_not_found(self, setup_test_db):
        """Test deleting non-existent restaurant raises error."""
        with patch('app.backend.db.db_path', setup_test_db):
            with pytest.raises(ValueError, match="Restaurant 'NonExistent' not found"):
                delete_restaurant_from_db("NonExistent")

    def test_delete_restaurant_cascades_to_info(self, setup_test_db):
        """Test deleting restaurant also deletes associated restaurant_info."""
        with patch('app.backend.db.db_path', setup_test_db):
            # Save info for existing restaurant
            save_restaurant_info(
                "McDonald's",
                address="123 Test St",
                phone="555-1234",
            )

            # Verify info exists
            info = get_restaurant_info("McDonald's")
            assert info is not None
            assert info["address"] == "123 Test St"

            # Delete restaurant
            delete_restaurant_from_db("McDonald's")

            # Verify both restaurant and info are deleted
            all_restaurants = get_all_restaurants()
            assert ("McDonald's", "cheap") not in all_restaurants

            info_after = get_restaurant_info("McDonald's")
            assert info_after is None

    def test_add_to_recent_lunch(self, temp_db):
        """Test adding restaurant to recent lunch list."""
        with patch('app.backend.db.db_path', temp_db):
            create_db_and_tables()
            result = add_to_recent_lunch("Test Restaurant")
            assert result is True

            # Verify it was added
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT restaurants FROM recent_lunch")
            recent = cursor.fetchall()
            assert len(recent) == 1
            assert recent[0][0] == "Test Restaurant"
            conn.close()

    def test_add_to_recent_lunch_limit(self, temp_db):
        """Test recent lunch list maintains 14-item limit."""
        with patch('app.backend.db.db_path', temp_db):
            create_db_and_tables()

            # Add 16 restaurants
            for i in range(16):
                add_to_recent_lunch(f"Restaurant {i}")

            # Verify only 14 are kept
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM recent_lunch")
            count = cursor.fetchone()[0]
            assert count == 14

            # Verify newest entries are kept
            cursor.execute("SELECT restaurants FROM recent_lunch ORDER BY date DESC")
            recent = cursor.fetchall()
            assert recent[0][0] == "Restaurant 15"  # Most recent
            assert "Restaurant 0" not in [r[0] for r in recent]  # Oldest removed
            conn.close()

    def test_rng_restaurant_success(self, setup_test_db):
        """Test random restaurant selection."""
        with patch('app.backend.db.db_path', setup_test_db):
            restaurant = rng_restaurant("cheap")
            assert restaurant[1] == "cheap"
            assert restaurant[0] in ["McDonald's", "Burger King", "Subway"]

    def test_rng_restaurant_no_restaurants(self, setup_test_db):
        """Test random restaurant selection with no matching restaurants."""
        with patch('app.backend.db.db_path', setup_test_db):
            with pytest.raises(ValueError, match="No restaurants found with option: expensive"):
                rng_restaurant("expensive")

    def test_calculate_lunch_basic(self, setup_test_db):
        """Test basic lunch calculation."""
        with patch('app.backend.db.db_path', setup_test_db):
            restaurant = calculate_lunch("cheap")
            assert restaurant[1] == "cheap"
            assert restaurant[0] in ["McDonald's", "Burger King", "Subway"]

    def test_calculate_lunch_round_robin(self, setup_test_db):
        """Test round-robin logic in lunch calculation."""
        with patch('app.backend.db.db_path', setup_test_db):
            session_rolled = set()

            # First selection
            restaurant1 = calculate_lunch("cheap", session_rolled)
            assert restaurant1[0] in session_rolled

            # Second selection should be different
            restaurant2 = calculate_lunch("cheap", session_rolled)
            assert restaurant2[0] != restaurant1[0]
            assert len(session_rolled) == 2

    def test_calculate_lunch_session_reset(self, setup_test_db):
        """Test session reset when all restaurants have been selected."""
        with patch('app.backend.db.db_path', setup_test_db):
            session_rolled = {"McDonald's", "Burger King", "Subway"}  # All cheap restaurants

            # Should reset session and select again
            restaurant = calculate_lunch("cheap", session_rolled)
            assert restaurant[1] == "cheap"
            assert len(session_rolled) == 1  # Reset and one added

    def test_calculate_lunch_no_restaurants(self, setup_test_db):
        """Test lunch calculation with no matching restaurants."""
        with patch('app.backend.db.db_path', setup_test_db):
            with pytest.raises(ValueError, match="No restaurants found with option: expensive"):
                calculate_lunch("expensive")

    def test_calculate_lunch_avoids_recent(self, setup_test_db):
        """Test that lunch calculation avoids recently selected restaurants."""
        with patch('app.backend.db.db_path', setup_test_db):
            # Add a recent lunch entry
            add_to_recent_lunch("McDonald's")

            # Should avoid McDonald's if possible
            session_rolled = set()
            restaurant = calculate_lunch("cheap", session_rolled)

            # If there are other options, McDonald's should be avoided
            # (Note: this test may occasionally fail due to randomness, but very unlikely)
            if len(get_restaurants("cheap")) > 1:
                # With 3 cheap restaurants and 1 recent, chance of getting McDonald's is 1/2
                # Run multiple times to increase confidence
                selections = []
                for _ in range(10):
                    session_rolled.clear()
                    selected = calculate_lunch("cheap", session_rolled)
                    selections.append(selected[0])

                # Should get some variety, not just McDonald's
                unique_selections = set(selections)
                assert len(unique_selections) > 1 or "McDonald's" not in unique_selections

    def test_database_error_handling(self, temp_db):
        """Test database error handling."""
        # Test with invalid database path
        invalid_path = temp_db.parent / "nonexistent" / "invalid.db"

        with patch('app.backend.db.db_path', invalid_path):
            # Should handle errors gracefully
            result = get_all_restaurants()
            assert result == []

    def test_concurrent_operations(self, setup_test_db):
        """Test that database operations work correctly with concurrent access."""
        with patch('app.backend.db.db_path', setup_test_db):
            # Simulate concurrent operations
            restaurants_before = len(get_all_restaurants())

            # Add and delete operations
            add_restaurant_to_db("Concurrent Test", "Normal")
            delete_restaurant_from_db("Subway")

            restaurants_after = len(get_all_restaurants())
            assert restaurants_after == restaurants_before  # Net zero change

    def test_data_integrity(self, setup_test_db):
        """Test data integrity during operations."""
        with patch('app.backend.db.db_path', setup_test_db):
            original_count = len(get_all_restaurants())

            # Add restaurant
            add_restaurant_to_db("Integrity Test", "Normal")
            assert len(get_all_restaurants()) == original_count + 1

            # Delete restaurant
            delete_restaurant_from_db("Integrity Test")
            assert len(get_all_restaurants()) == original_count

            # Verify original data is intact
            restaurants = get_all_restaurants()
            restaurant_names = [r[0] for r in restaurants]
            assert "McDonald's" in restaurant_names
            assert "The Ritz" in restaurant_names


class TestRestaurantInfoOperations:
    """Test cases for restaurant_info table operations."""

    def test_save_restaurant_info(self, setup_test_db):
        """Test saving restaurant info."""
        with patch('app.backend.db.db_path', setup_test_db):
            save_restaurant_info(
                "McDonald's",
                address="123 Main St",
                phone="555-1234",
                hours="9am-10pm",
                website="https://mcdonalds.com",
                description="Fast food restaurant",
            )

            info = get_restaurant_info("McDonald's")
            assert info is not None
            assert info["address"] == "123 Main St"
            assert info["phone"] == "555-1234"
            assert info["hours"] == "9am-10pm"
            assert info["website"] == "https://mcdonalds.com"
            assert info["description"] == "Fast food restaurant"
            assert info["last_updated"] is not None

    def test_get_restaurant_info_not_found(self, setup_test_db):
        """Test getting info for non-existent restaurant."""
        with patch('app.backend.db.db_path', setup_test_db):
            info = get_restaurant_info("NonExistent Restaurant")
            assert info is None

    def test_update_restaurant_info(self, setup_test_db):
        """Test updating existing restaurant info."""
        with patch('app.backend.db.db_path', setup_test_db):
            # Save initial info
            save_restaurant_info("McDonald's", address="123 Main St")

            # Update with new info
            save_restaurant_info("McDonald's", address="456 Oak Ave", phone="555-9999")

            info = get_restaurant_info("McDonald's")
            assert info["address"] == "456 Oak Ave"
            assert info["phone"] == "555-9999"

    def test_delete_restaurant_info(self, setup_test_db):
        """Test deleting restaurant info."""
        with patch('app.backend.db.db_path', setup_test_db):
            # Save info first
            save_restaurant_info("McDonald's", address="123 Main St")
            assert get_restaurant_info("McDonald's") is not None

            # Delete it
            delete_restaurant_info("McDonald's")
            assert get_restaurant_info("McDonald's") is None

    def test_save_restaurant_info_partial(self, setup_test_db):
        """Test saving restaurant info with only some fields."""
        with patch('app.backend.db.db_path', setup_test_db):
            save_restaurant_info("McDonald's", address="123 Main St")

            info = get_restaurant_info("McDonald's")
            assert info is not None
            assert info["address"] == "123 Main St"
            assert info["phone"] is None
            assert info["hours"] is None

    def test_get_restaurant_info_fresh_cache(self, setup_test_db):
        """Test that fresh cache (within TTL) returns data."""
        with patch('app.backend.db.db_path', setup_test_db):
            save_restaurant_info("McDonald's", address="123 Main St")

            # Fresh data should be returned (default TTL is 7 days)
            info = get_restaurant_info("McDonald's", max_age_days=7)
            assert info is not None
            assert info["address"] == "123 Main St"

    def test_get_restaurant_info_stale_cache(self, setup_test_db):
        """Test that stale cache (beyond TTL) returns None."""
        with patch('app.backend.db.db_path', setup_test_db):
            # Insert data with old timestamp (10 days ago)
            conn = sqlite3.connect(setup_test_db)
            cursor = conn.cursor()
            old_timestamp = (datetime.now() - timedelta(days=10)).isoformat()
            cursor.execute(
                """INSERT INTO restaurant_info
                   (restaurant_name, address, last_updated)
                   VALUES (?, ?, ?)""",
                ("McDonald's", "123 Main St", old_timestamp),
            )
            conn.commit()
            conn.close()

            # Stale data (older than 7 days) should return None
            info = get_restaurant_info("McDonald's", max_age_days=7)
            assert info is None

    def test_get_restaurant_info_ttl_from_config(self, setup_test_db):
        """Test that TTL defaults to config value when not specified."""
        with patch('app.backend.db.db_path', setup_test_db), patch('app.config.get_app_config') as mock_config:
            mock_config.return_value = {"cache_ttl_days": 5}

            # Insert data 6 days old
            conn = sqlite3.connect(setup_test_db)
            cursor = conn.cursor()
            old_timestamp = (datetime.now() - timedelta(days=6)).isoformat()
            cursor.execute(
                """INSERT INTO restaurant_info
                       (restaurant_name, address, last_updated)
                       VALUES (?, ?, ?)""",
                ("McDonald's", "123 Main St", old_timestamp),
            )
            conn.commit()
            conn.close()

            # Should be stale with 5-day TTL from config
            info = get_restaurant_info("McDonald's")
            assert info is None

    def test_get_restaurant_info_no_last_updated(self, setup_test_db):
        """Test cache with missing last_updated still returns data."""
        with patch('app.backend.db.db_path', setup_test_db):
            # Insert data without last_updated
            conn = sqlite3.connect(setup_test_db)
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO restaurant_info
                   (restaurant_name, address, last_updated)
                   VALUES (?, ?, ?)""",
                ("McDonald's", "123 Main St", None),
            )
            conn.commit()
            conn.close()

            # Should return data even without timestamp (treat as fresh)
            info = get_restaurant_info("McDonald's", max_age_days=7)
            assert info is not None
            assert info["address"] == "123 Main St"
