"""
Unit tests for the RestaurantService class.
Tests business logic without database dependencies.
"""

import pytest
from backend.service import RestaurantService
from unittest.mock import Mock


class TestRestaurantService:
    """Test cases for RestaurantService business logic."""
    
    def test_initialization(self, mock_db_manager):
        """Test service initialization."""
        service = RestaurantService(mock_db_manager)
        assert service.db == mock_db_manager
        assert "cheap" in service.session_rolled_restaurants
        assert "Normal" in service.session_rolled_restaurants
        assert isinstance(service.session_rolled_restaurants["cheap"], set)
        assert isinstance(service.session_rolled_restaurants["Normal"], set)
    
    def test_initialize_calls_db_setup(self, mock_db_manager):
        """Test that initialize calls database setup."""
        service = RestaurantService(mock_db_manager)
        service.initialize()
        mock_db_manager.create_db_and_tables.assert_called_once()
    
    def test_get_all_restaurants(self, mock_db_manager):
        """Test getting all restaurants."""
        service = RestaurantService(mock_db_manager)
        result = service.get_all_restaurants()
        
        mock_db_manager.get_all_restaurants.assert_called_once()
        assert result == [
            ("McDonald's", "cheap"),
            ("Burger King", "cheap"),
            ("The Ritz", "Normal"),
            ("Fine Dining", "Normal"),
        ]
    
    def test_get_restaurants_by_category(self, mock_db_manager):
        """Test getting restaurants by category."""
        service = RestaurantService(mock_db_manager)
        result = service.get_restaurants_by_category("cheap")
        
        mock_db_manager.get_restaurants.assert_called_once_with("cheap")
        assert result == [("McDonald's", "cheap"), ("Burger King", "cheap")]
    
    def test_add_restaurant_success(self, mock_db_manager):
        """Test successful restaurant addition."""
        service = RestaurantService(mock_db_manager)
        result = service.add_restaurant("New Place", "Normal")
        
        mock_db_manager.add_restaurant_to_db.assert_called_once_with("New Place", "Normal")
        assert result == "Added restaurant: New Place (Normal)"
    
    def test_add_restaurant_duplicate_error(self, mock_db_manager):
        """Test adding duplicate restaurant raises ValueError."""
        mock_db_manager.add_restaurant_to_db.side_effect = ValueError("Restaurant 'New Place' already exists")
        service = RestaurantService(mock_db_manager)
        
        with pytest.raises(ValueError, match="Restaurant 'New Place' already exists"):
            service.add_restaurant("New Place", "Normal")
    
    def test_add_restaurant_general_error(self, mock_db_manager):
        """Test general error during restaurant addition."""
        mock_db_manager.add_restaurant_to_db.side_effect = Exception("Database error")
        service = RestaurantService(mock_db_manager)
        
        with pytest.raises(Exception, match="Error adding restaurant: Database error"):
            service.add_restaurant("New Place", "Normal")
    
    def test_delete_restaurant_success(self, mock_db_manager):
        """Test successful restaurant deletion."""
        service = RestaurantService(mock_db_manager)
        result = service.delete_restaurant("McDonald's")
        
        mock_db_manager.delete_restaurant_from_db.assert_called_once_with("McDonald's")
        assert result == "Deleted restaurant: McDonald's"
    
    def test_delete_restaurant_not_found_error(self, mock_db_manager):
        """Test deleting non-existent restaurant raises ValueError."""
        mock_db_manager.delete_restaurant_from_db.side_effect = ValueError("Restaurant 'NonExistent' not found")
        service = RestaurantService(mock_db_manager)
        
        with pytest.raises(ValueError, match="Restaurant 'NonExistent' not found"):
            service.delete_restaurant("NonExistent")
    
    def test_delete_restaurant_general_error(self, mock_db_manager):
        """Test general error during restaurant deletion."""
        mock_db_manager.delete_restaurant_from_db.side_effect = Exception("Database error")
        service = RestaurantService(mock_db_manager)
        
        with pytest.raises(Exception, match="Error deleting restaurant: Database error"):
            service.delete_restaurant("McDonald's")
    
    def test_select_restaurant_success(self, mock_db_manager):
        """Test successful restaurant selection."""
        service = RestaurantService(mock_db_manager)
        result = service.select_restaurant("cheap")
        
        mock_db_manager.calculate_lunch.assert_called_once_with("cheap", service.session_rolled_restaurants["cheap"])
        assert result == ("McDonald's", "cheap")
    
    def test_select_restaurant_no_restaurants_found(self, mock_db_manager):
        """Test restaurant selection when no restaurants found."""
        mock_db_manager.calculate_lunch.side_effect = ValueError("No restaurants found with option: expensive")
        service = RestaurantService(mock_db_manager)
        
        with pytest.raises(ValueError, match="No expensive restaurants available. Add some restaurants first!"):
            service.select_restaurant("expensive")
    
    def test_select_restaurant_general_error(self, mock_db_manager):
        """Test general error during restaurant selection."""
        mock_db_manager.calculate_lunch.side_effect = Exception("Database error")
        service = RestaurantService(mock_db_manager)
        
        with pytest.raises(Exception, match="Error selecting restaurant: Database error"):
            service.select_restaurant("cheap")
    
    def test_select_restaurant_default_category(self, mock_db_manager):
        """Test restaurant selection with default category."""
        service = RestaurantService(mock_db_manager)
        result = service.select_restaurant()
        
        mock_db_manager.calculate_lunch.assert_called_once_with("Normal", service.session_rolled_restaurants["Normal"])
        assert result == ("McDonald's", "cheap")
    
    def test_get_random_restaurant_success(self, mock_db_manager):
        """Test successful random restaurant selection."""
        service = RestaurantService(mock_db_manager)
        result = service.get_random_restaurant("cheap")
        
        mock_db_manager.rng_restaurant.assert_called_once_with("cheap")
        assert result == ("McDonald's", "cheap")
    
    def test_get_random_restaurant_error(self, mock_db_manager):
        """Test error during random restaurant selection."""
        mock_db_manager.rng_restaurant.side_effect = ValueError("No restaurants found")
        service = RestaurantService(mock_db_manager)
        
        with pytest.raises(ValueError, match="No restaurants found"):
            service.get_random_restaurant("expensive")
    
    def test_reset_session_for_category(self, mock_db_manager):
        """Test resetting session for specific category."""
        service = RestaurantService(mock_db_manager)
        service.session_rolled_restaurants["cheap"].add("McDonald's")
        service.session_rolled_restaurants["cheap"].add("Burger King")
        
        service.reset_session_for_category("cheap")
        
        assert len(service.session_rolled_restaurants["cheap"]) == 0
        assert "Normal" in service.session_rolled_restaurants  # Other categories unchanged
    
    def test_reset_session_for_invalid_category(self, mock_db_manager):
        """Test resetting session for invalid category."""
        service = RestaurantService(mock_db_manager)
        service.reset_session_for_category("invalid")
        # Should not raise error, just do nothing
    
    def test_reset_all_sessions(self, mock_db_manager):
        """Test resetting all sessions."""
        service = RestaurantService(mock_db_manager)
        service.session_rolled_restaurants["cheap"].add("McDonald's")
        service.session_rolled_restaurants["Normal"].add("The Ritz")
        
        service.reset_all_sessions()
        
        assert len(service.session_rolled_restaurants["cheap"]) == 0
        assert len(service.session_rolled_restaurants["Normal"]) == 0
    
    def test_session_state_isolation(self, mock_db_manager):
        """Test that session state is properly isolated between categories."""
        service = RestaurantService(mock_db_manager)
        
        # Simulate rolling restaurants
        service.session_rolled_restaurants["cheap"].add("McDonald's")
        service.session_rolled_restaurants["Normal"].add("The Ritz")
        
        # Each category should maintain its own state
        assert "McDonald's" in service.session_rolled_restaurants["cheap"]
        assert "McDonald's" not in service.session_rolled_restaurants["Normal"]
        assert "The Ritz" in service.session_rolled_restaurants["Normal"]
        assert "The Ritz" not in service.session_rolled_restaurants["cheap"]