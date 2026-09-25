import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "kabadiwala.db")


def create_database():

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # ==========================================
    # USERS TABLE
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mobile TEXT UNIQUE NOT NULL,
            location TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    # ==========================================
    # COLLECTION REQUESTS TABLE
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS collection_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            waste_type TEXT NOT NULL,
            weight REAL DEFAULT 0,
            quantity REAL DEFAULT 0,
            location TEXT NOT NULL,
            description TEXT,
            collection_date TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ==========================================
    # WASTE TABLE
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS waste (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            collector_id INTEGER NOT NULL,
            material TEXT NOT NULL,
            weight REAL NOT NULL,
            location TEXT NOT NULL,
            status TEXT DEFAULT 'Collected',
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            recycler_id INTEGER,
            recycler_status TEXT DEFAULT 'Not Sent',
            FOREIGN KEY (collector_id) REFERENCES users(id)
        )
    """)

    # ==========================================
    # COLLECTOR LOCATION TABLE
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS collector_locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            collector_id INTEGER NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (collector_id) REFERENCES users(id)
        )
    """)

    connection.commit()
    connection.close()

    print("Database created successfully!")


if __name__ == "__main__":
    create_database()
