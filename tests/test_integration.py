"""
Integration tests for the complete restaurant management system.
Tests the full flow from service layer to database operations.
"""

import pytest
from app.backend.db import (
    add_restaurant_to_db,
    calculate_lunch,
    create_db_and_tables,
    delete_restaurant_from_db,
    get_all_restaurants,
    get_restaurants,
    rng_restaurant,
)
from app.backend.service import RestaurantService
from unittest.mock import patch


class RealDatabaseManager:
    """Real database manager for integration testing."""
    
    def create_db_and_tables(self):
        return create_db_and_tables()
    
    def get_all_restaurants(self):
        return get_all_restaurants()
    
    def get_restaurants(self, option):
        return get_restaurants(option)
    
    def add_restaurant_to_db(self, name, option):
        return add_restaurant_to_db(name, option)
    
    def delete_restaurant_from_db(self, name):
        return delete_restaurant_from_db(name)
    
    def calculate_lunch(self, option, session_rolled):
        return calculate_lunch(option, session_rolled)
    
    def rng_restaurant(self, option):
        return rng_restaurant(option)


class TestIntegrationOperations:
    """Integration tests for all restaurant operations."""
    
    def setup_method(self):
        """Setup fresh database for each test method."""
        import sqlite3
        import tempfile
        
        # Create a temporary database for this test
        temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db_path = temp_file.name
        temp_file.close()
        
        # Create fresh database with sample data
        conn = sqlite3.connect(self.temp_db_path)
        cursor = conn.cursor()
        
        # Create tables
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
        
        # Insert fresh sample data for each test
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
        
        # Start the patch for this test
        self.patcher = patch('app.backend.db.db_path', self.temp_db_path)
        self.patcher.start()
        
        # Initialize service
        self.db_manager = RealDatabaseManager()
        self.service = RestaurantService(self.db_manager)
        self.service.initialize()
    
    def teardown_method(self):
        """Clean up after each test method."""
        # Stop the patch
        self.patcher.stop()
        
        # Clean up temporary database file
        import os
        if os.path.exists(self.temp_db_path):
            os.unlink(self.temp_db_path)
    
    def test_complete_restaurant_lifecycle(self):
        """Test complete lifecycle: list -> add -> list -> delete -> list."""
        # Initial state
        initial_restaurants = self.service.get_all_restaurants()
        initial_count = len(initial_restaurants)
        assert initial_count == 6
        
        # Add new restaurant
        add_result = self.service.add_restaurant("Integration Test Restaurant", "Normal")
        assert "Added restaurant: Integration Test Restaurant (Normal)" in add_result
        
        # Verify addition
        after_add = self.service.get_all_restaurants()
        assert len(after_add) == initial_count + 1
        restaurant_names = [r[0] for r in after_add]
        assert "Integration Test Restaurant" in restaurant_names
        
        # Delete the restaurant
        delete_result = self.service.delete_restaurant("Integration Test Restaurant")
        assert "Deleted restaurant: Integration Test Restaurant" in delete_result
        
        # Verify deletion
        after_delete = self.service.get_all_restaurants()
        assert len(after_delete) == initial_count
        restaurant_names = [r[0] for r in after_delete]
        assert "Integration Test Restaurant" not in restaurant_names
    
    def test_roll_operation_with_real_data(self):
        """Test restaurant selection with real database operations."""
        # Test rolling cheap restaurants
        cheap_restaurants = self.service.get_restaurants_by_category("cheap")
        assert len(cheap_restaurants) == 3
        
        selected_restaurant = self.service.select_restaurant("cheap")
        assert selected_restaurant[1] == "cheap"
        assert selected_restaurant[0] in [r[0] for r in cheap_restaurants]
        
        # Verify session tracking
        assert selected_restaurant[0] in self.service.session_rolled_restaurants["cheap"]
    
    def test_round_robin_behavior_integration(self):
        """Test full round-robin behavior with session management."""
        # Get all cheap restaurants
        cheap_restaurants = self.service.get_restaurants_by_category("cheap")
        cheap_names = {r[0] for r in cheap_restaurants}
        
        selected_names = set()
        
        # Select restaurants until we've gone through all
        for _ in range(len(cheap_restaurants)):
            restaurant = self.service.select_restaurant("cheap")
            selected_names.add(restaurant[0])
        
        # Should have selected all cheap restaurants
        assert selected_names == cheap_names
        assert len(self.service.session_rolled_restaurants["cheap"]) == len(cheap_restaurants)
    
    def test_session_reset_integration(self):
        """Test session reset when all restaurants have been selected."""
        # Get all Normal restaurants
        normal_restaurants = self.service.get_restaurants_by_category("Normal")
        
        # Select all Normal restaurants
        for _ in range(len(normal_restaurants)):
            self.service.select_restaurant("Normal")
        
        # Session should have all restaurants
        assert len(self.service.session_rolled_restaurants["Normal"]) == len(normal_restaurants)
        
        # Next selection should reset session
        next_restaurant = self.service.select_restaurant("Normal")
        assert next_restaurant[1] == "Normal"
        # Session should be reset and have only the new selection
        assert len(self.service.session_rolled_restaurants["Normal"]) == 1
    
    def test_category_isolation_integration(self):
        """Test that different categories maintain separate sessions."""
        # Select from cheap category
        cheap_restaurant = self.service.select_restaurant("cheap")
        cheap_session_size = len(self.service.session_rolled_restaurants["cheap"])
        normal_session_size = len(self.service.session_rolled_restaurants["Normal"])
        
        assert cheap_session_size == 1
        assert normal_session_size == 0
        
        # Select from Normal category
        normal_restaurant = self.service.select_restaurant("Normal")
        
        # Both sessions should be independent
        assert len(self.service.session_rolled_restaurants["cheap"]) == 1
        assert len(self.service.session_rolled_restaurants["Normal"]) == 1
        assert cheap_restaurant[0] in self.service.session_rolled_restaurants["cheap"]
        assert normal_restaurant[0] in self.service.session_rolled_restaurants["Normal"]
        assert cheap_restaurant != normal_restaurant
    
    def test_error_handling_integration(self):
        """Test error handling in real scenarios."""
        # Test adding duplicate restaurant
        with pytest.raises(ValueError, match="McDonald's.*already exists"):
            self.service.add_restaurant("McDonald's", "cheap")
        
        # Test deleting non-existent restaurant
        with pytest.raises(ValueError, match="not found"):
            self.service.delete_restaurant("Non-Existent Restaurant")
        
        # Test selecting from empty category
        # First delete all cheap restaurants
        cheap_restaurants = self.service.get_restaurants_by_category("cheap")
        for restaurant in cheap_restaurants:
            self.service.delete_restaurant(restaurant[0])
        
        # Now trying to select should raise error
        with pytest.raises(ValueError, match="No cheap restaurants available"):
            self.service.select_restaurant("cheap")
    
    def test_add_delete_different_categories(self):
        """Test adding and deleting restaurants from different categories."""
        initial_count = len(self.service.get_all_restaurants())
        
        # Add restaurants to both categories
        self.service.add_restaurant("New Cheap Place", "cheap")
        self.service.add_restaurant("New Fancy Place", "Normal")
        
        assert len(self.service.get_all_restaurants()) == initial_count + 2
        
        # Verify they're in correct categories
        cheap_restaurants = self.service.get_restaurants_by_category("cheap")
        normal_restaurants = self.service.get_restaurants_by_category("Normal")
        
        cheap_names = [r[0] for r in cheap_restaurants]
        normal_names = [r[0] for r in normal_restaurants]
        
        assert "New Cheap Place" in cheap_names
        assert "New Fancy Place" in normal_names
        assert "New Cheap Place" not in normal_names
        assert "New Fancy Place" not in cheap_names
        
        # Delete them
        self.service.delete_restaurant("New Cheap Place")
        self.service.delete_restaurant("New Fancy Place")
        
        assert len(self.service.get_all_restaurants()) == initial_count
    
    def test_session_management_with_modifications(self):
        """Test session behavior when restaurants are added/deleted during session."""
        # Ensure we have enough cheap restaurants for the test
        initial_cheap = self.service.get_restaurants_by_category("cheap")
        if len(initial_cheap) < 2:
            # Add restaurants to ensure we have enough for the test
            self.service.add_restaurant("Test Cheap 1", "cheap")
            self.service.add_restaurant("Test Cheap 2", "cheap")
        
        # Start a session
        selected1 = self.service.select_restaurant("cheap")
        session_before = self.service.session_rolled_restaurants["cheap"].copy()
        
        # Add a new cheap restaurant
        self.service.add_restaurant("Mid-Session Restaurant", "cheap")
        
        # Session should still be valid
        selected2 = self.service.select_restaurant("cheap")
        assert selected1[0] != selected2[0]
        
        # Clean up by deleting only the restaurant we added
        self.service.delete_restaurant("Mid-Session Restaurant")
        
        # Should still be able to select from remaining restaurants
        selected3 = self.service.select_restaurant("cheap")
        assert selected3 is not None
    
    def test_random_vs_calculated_selection(self):
        """Test difference between random and calculated (round-robin) selection."""
        # Ensure we have enough restaurants for the test
        cheap_restaurants = self.service.get_restaurants_by_category("cheap")
        if len(cheap_restaurants) < 3:
            # Add restaurants to ensure we have enough for the test
            needed = 3 - len(cheap_restaurants)
            for i in range(needed):
                self.service.add_restaurant(f"Test Cheap Random {i}", "cheap")
        
        # Get current cheap restaurants
        current_cheap = self.service.get_restaurants_by_category("cheap")
        cheap_count = len(current_cheap)
        
        # Get random restaurant multiple times
        random_selections = []
        for _ in range(5):
            random_restaurant = self.service.get_random_restaurant("cheap")
            random_selections.append(random_restaurant[0])
        
        # Reset session for clean test
        self.service.reset_session_for_category("cheap")
        
        # Get calculated restaurants
        calculated_selections = []
        for _ in range(min(cheap_count, 3)):  # Take the minimum of available or 3
            calculated_restaurant = self.service.select_restaurant("cheap")
            calculated_selections.append(calculated_restaurant[0])
        
        # Calculated selections should be unique (round-robin)
        assert len(set(calculated_selections)) == len(calculated_selections)
        
        # Random selections might have duplicates (but all should be valid)
        cheap_names = [r[0] for r in self.service.get_restaurants_by_category("cheap")]
        for selection in random_selections:
            assert selection in cheap_names
    
    def test_concurrent_session_operations(self):
        """Test behavior with multiple rapid operations."""
        # Rapidly add and select restaurants
        operations_count = 10
        added_restaurants = []
        
        for i in range(operations_count):
            restaurant_name = f"Rapid Test {i}"
            self.service.add_restaurant(restaurant_name, "Normal")
            added_restaurants.append(restaurant_name)
            
            # Select after each addition
            selected = self.service.select_restaurant("Normal")
            assert selected[1] == "Normal"
        
        # Verify all were added
        all_restaurants = self.service.get_all_restaurants()
        all_names = [r[0] for r in all_restaurants]
        for added_name in added_restaurants:
            assert added_name in all_names
        
        # Clean up
        for restaurant_name in added_restaurants:
            self.service.delete_restaurant(restaurant_name)
    
    def test_state_persistence_across_operations(self):
        """Test that session state persists correctly across different operations."""
        # Select a restaurant
        first_selection = self.service.select_restaurant("Normal")
        
        # Perform other operations
        self.service.add_restaurant("Temp Restaurant", "cheap")
        all_restaurants = self.service.get_all_restaurants()
        self.service.delete_restaurant("Temp Restaurant")
        
        # Session state should still be maintained
        assert first_selection[0] in self.service.session_rolled_restaurants["Normal"]
        
        # Next selection should still follow round-robin
        second_selection = self.service.select_restaurant("Normal")
        assert second_selection[0] != first_selection[0]
        assert len(self.service.session_rolled_restaurants["Normal"]) == 2