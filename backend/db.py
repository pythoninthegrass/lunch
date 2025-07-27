import csv
import random
import sqlite3
from datetime import datetime
from pathlib import Path

# Define paths
db_path = Path(__file__).parent.parent / "data" / "lunch.db"
restaurants_csv = Path(__file__).parent.parent / "data" / "restaurants.csv"


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
            with open(restaurants_csv) as f:
                csv_reader = csv.DictReader(f)
                for row in csv_reader:
                    cursor.execute(
                        "INSERT OR IGNORE INTO lunch_list VALUES (?, ?)",
                        (row['restaurant'], row['option']),
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
            (option,),
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
        cursor.execute("INSERT INTO lunch_list VALUES (?, ?)", (name, option))
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
        cursor.execute("DELETE FROM lunch_list WHERE restaurants = ?", (name,))
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
                (count - 13,),  # Keep 14 entries
            )

        # Add the new restaurant
        now = datetime.now().isoformat()
        cursor.execute("INSERT OR REPLACE INTO recent_lunch VALUES (?, ?)", (restaurant_name, now))

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


def calculate_lunch(option="Normal", session_rolled=None):
    """Select a restaurant using round-robin logic within the session"""
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all restaurants with the specified option
        cursor.execute(
            "SELECT restaurants, option FROM lunch_list WHERE LOWER(option) = LOWER(?)",
            (option,),
        )
        restaurants = cursor.fetchall()

        if not restaurants:
            raise ValueError(f"No restaurants found with option: {option}")

        # Initialize session_rolled if not provided
        if session_rolled is None:
            session_rolled = set()

        # Find restaurants not yet rolled in this session
        unrolled = [r for r in restaurants if r[0] not in session_rolled]

        # If all restaurants have been rolled, reset the session for this option
        if not unrolled:
            session_rolled.clear()
            unrolled = restaurants

        # Get the most recently selected restaurant to avoid immediate repetition
        cursor.execute("""
            SELECT restaurants FROM recent_lunch 
            ORDER BY date DESC 
            LIMIT 1
        """)
        last_result = cursor.fetchone()
        last_restaurant = last_result[0] if last_result else None

        # Filter out the last restaurant from unrolled options
        available = [r for r in unrolled if r[0] != last_restaurant]

        # If only the last restaurant is left unrolled, we have to use it
        if not available and unrolled:
            available = unrolled

        # If no restaurants available (shouldn't happen), use all
        if not available:
            available = restaurants

        # Select a random restaurant from available options
        chosen = random.choice(available)

        # Add to session rolled set
        session_rolled.add(chosen[0])

        # Add to recent lunches database
        add_to_recent_lunch(chosen[0])

        return chosen
    except Exception as e:
        print(f"Error calculating lunch: {e}")
        # Re-raise if it's a ValueError about no restaurants
        if isinstance(e, ValueError) and "No restaurants found" in str(e):
            raise e
        # Fallback to simple random selection
        restaurants = get_restaurants(option)
        if not restaurants:
            raise ValueError(f"No restaurants found with option: {option}")
        return random.choice(restaurants)
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    """Test function"""
    create_db_and_tables()
    print("All restaurants:", get_all_restaurants())
    print("Normal restaurants:", get_restaurants("Normal"))
    print("Random cheap restaurant:", rng_restaurant("cheap"))
    print("Calculated lunch:", calculate_lunch())
