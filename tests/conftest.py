"""
Test configuration and fixtures for the lunch application tests.
"""

import pytest
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import Mock


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_path = Path(temp_file.name)
    temp_file.close()
    
    yield temp_path
    
    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def mock_db_manager():
    """Create a mock database manager for unit testing."""
    mock = Mock()
    mock.create_db_and_tables.return_value = None
    mock.get_all_restaurants.return_value = [
        ("McDonald's", "cheap"),
        ("Burger King", "cheap"),
        ("The Ritz", "Normal"),
        ("Fine Dining", "Normal"),
    ]
    mock.get_restaurants.return_value = [("McDonald's", "cheap"), ("Burger King", "cheap")]
    mock.add_restaurant_to_db.return_value = True
    mock.delete_restaurant_from_db.return_value = True
    mock.calculate_lunch.return_value = ("McDonald's", "cheap")
    mock.rng_restaurant.return_value = ("McDonald's", "cheap")
    
    return mock


@pytest.fixture
def sample_restaurants():
    """Sample restaurant data for testing."""
    return [
        ("McDonald's", "cheap"),
        ("Burger King", "cheap"),
        ("Subway", "cheap"),
        ("The Ritz", "Normal"),
        ("Fine Dining", "Normal"),
        ("Steakhouse", "Normal"),
    ]


@pytest.fixture
def setup_test_db(temp_db):
    """Setup a test database with sample data."""
    conn = sqlite3.connect(temp_db)
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
    
    # Insert sample data
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
    
    return temp_db