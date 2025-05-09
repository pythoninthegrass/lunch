#!/usr/bin/env python3

import random
import csv
import sqlite3
from datetime import datetime
from pathlib import Path

# Define paths
db_path = Path(__file__).parent / "lunch.db"
restaurants_csv = Path(__file__).parent / "restaurants.csv"

def create_db_and_tables():
    """Create database and tables if they don't exist"""
    conn = None
    try:
        # Create a connection
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create tables if they don't exist
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

        # Check if lunch_list is empty
        cursor.execute("SELECT COUNT(*) FROM lunch_list")
        count = cursor.fetchone()[0]

        # If table is empty, import data from CSV
        if count == 0 and restaurants_csv.exists():
            with open(restaurants_csv, 'r') as f:
                csv_reader = csv.DictReader(f)
                for row in csv_reader:
                    cursor.execute(
                        "INSERT OR IGNORE INTO lunch_list VALUES (?, ?)",
                        (row['restaurant'], row['option'])
                    )

            print(f"Imported restaurants from {restaurants_csv}")

        conn.commit()

    except Exception as e:
        print(f"Error creating database: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def get_all_restaurants():
    """Get all restaurants from the database"""
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT restaurants, option FROM lunch_list ORDER BY restaurants")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error getting restaurants: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_restaurants(option):
    """Get restaurants filtered by option (cheap/Normal)"""
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT restaurants, option FROM lunch_list WHERE LOWER(option) = LOWER(?)",
            (option,)
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Error getting restaurants by option: {e}")
        return []
    finally:
        if conn:
            conn.close()

def rng_restaurant(option):
    """Get a random restaurant with the specified option"""
    restaurants = get_restaurants(option)
    if not restaurants:
        raise ValueError(f"No restaurants found with option: {option}")
    return random.choice(restaurants)

def add_restaurant_to_db(name, option):
    """Add a new restaurant to the database"""
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO lunch_list VALUES (?, ?)",
            (name, option)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        raise ValueError(f"Restaurant '{name}' already exists")
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

def delete_restaurant_from_db(name):
    """Delete a restaurant from the database"""
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM lunch_list WHERE restaurants = ?",
            (name,)
        )
        if cursor.rowcount == 0:
            raise ValueError(f"Restaurant '{name}' not found")
        conn.commit()
        return True
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

def add_to_recent_lunch(restaurant_name):
    """Add a restaurant to the recent lunch list"""
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if we have 14 or more recent lunches
        cursor.execute("SELECT COUNT(*) FROM recent_lunch")
        count = cursor.fetchone()[0]

        if count >= 14:
            # Delete the oldest entries
            cursor.execute(
                "DELETE FROM recent_lunch WHERE date IN (SELECT date FROM recent_lunch ORDER BY date ASC LIMIT ?)",
                (count - 13,)  # Keep 14 entries
            )

        # Add the new restaurant
        now = datetime.now().isoformat()
        cursor.execute(
            "INSERT OR REPLACE INTO recent_lunch VALUES (?, ?)",
            (restaurant_name, now)
        )

        conn.commit()
        return True
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error adding to recent lunch: {e}")
        return False
    finally:
        if conn:
            conn.close()

def calculate_lunch(option="Normal"):
    """Select a restaurant for lunch considering recent history"""
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all restaurants with the specified option
        cursor.execute(
            "SELECT restaurants, option FROM lunch_list WHERE LOWER(option) = LOWER(?)",
            (option,)
        )
        restaurants = cursor.fetchall()

        if not restaurants:
            raise ValueError(f"No restaurants found with option: {option}")

        # If fewer than 15 restaurants, just pick a random one
        if len(restaurants) < 15:
            chosen = random.choice(restaurants)
            add_to_recent_lunch(chosen[0])
            return chosen

        # Get recent lunch choices
        cursor.execute("SELECT restaurants FROM recent_lunch")
        recent = [row[0] for row in cursor.fetchall()]

        # Find restaurants that haven't been chosen recently
        available = [r for r in restaurants if r[0] not in recent]

        # If all have been chosen recently, pick a random one
        if not available:
            chosen = random.choice(restaurants)
        else:
            chosen = random.choice(available)

        # Add to recent lunches
        add_to_recent_lunch(chosen[0])

        return chosen
    except Exception as e:
        print(f"Error calculating lunch: {e}")
        # Fallback to simple random selection
        return random.choice(get_restaurants(option)) if get_restaurants(option) else None
    finally:
        if conn:
            conn.close()

def main():
    """Test function"""
    create_db_and_tables()
    print("All restaurants:", get_all_restaurants())
    print("Normal restaurants:", get_restaurants("Normal"))
    print("Random cheap restaurant:", rng_restaurant("cheap"))
    print("Calculated lunch:", calculate_lunch())

if __name__ == "__main__":
    main()
