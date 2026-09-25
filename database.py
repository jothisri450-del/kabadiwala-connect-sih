import sqlite3


# =========================================================
# DATABASE NAME
# =========================================================

DATABASE = "kabadiwala.db"


# =========================================================
# CREATE DATABASE
# =========================================================

def create_database():

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()


    # =====================================================
    # USERS TABLE
    # =====================================================

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


    # =====================================================
    # WASTE TABLE
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS waste (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            collector_id INTEGER NOT NULL,

            material TEXT NOT NULL,

            weight REAL NOT NULL,

            location TEXT NOT NULL,

            status TEXT NOT NULL,

            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (collector_id)
            REFERENCES users(id)

        )
    """)


    # =====================================================
    # COLLECTION REQUESTS TABLE
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS collection_requests (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            waste_type TEXT NOT NULL,

            weight REAL NOT NULL,

            location TEXT NOT NULL,

            collection_date TEXT NOT NULL,

            status TEXT DEFAULT 'Pending',

            collector_id INTEGER,

            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id)
            REFERENCES users(id),

            FOREIGN KEY (collector_id)
            REFERENCES users(id)

        )
    """)


    # =====================================================
    # PAYMENTS TABLE
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            collector_id INTEGER,

            amount REAL NOT NULL,

            payment_status TEXT DEFAULT 'Pending',

            payment_method TEXT,

            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id)
            REFERENCES users(id),

            FOREIGN KEY (collector_id)
            REFERENCES users(id)

        )
    """)


    # =====================================================
    # HANDOVER TABLE
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS handover (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            waste_id INTEGER NOT NULL,

            collector_id INTEGER NOT NULL,

            recycler_id INTEGER NOT NULL,

            qr_code TEXT,

            handover_status TEXT DEFAULT 'Pending',

            handover_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (waste_id)
            REFERENCES waste(id),

            FOREIGN KEY (collector_id)
            REFERENCES users(id),

            FOREIGN KEY (recycler_id)
            REFERENCES users(id)

        )
    """)


    # =====================================================
    # RECYCLING RECORDS TABLE
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recycling_records (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            waste_id INTEGER NOT NULL,

            recycler_id INTEGER NOT NULL,

            recycling_status TEXT DEFAULT 'Received',

            remarks TEXT,

            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (waste_id)
            REFERENCES waste(id),

            FOREIGN KEY (recycler_id)
            REFERENCES users(id)

        )
    """)


    # =====================================================
    # COMMIT CHANGES
    # =====================================================

    connection.commit()

    connection.close()


    print("----------------------------------------")
    print("Kabadiwala Connect Database")
    print("----------------------------------------")
    print("Database created successfully!")
    print()
    print("Tables created:")
    print("1. users")
    print("2. waste")
    print("3. collection_requests")
    print("4. payments")
    print("5. handover")
    print("6. recycling_records")
    print("----------------------------------------")


# =========================================================
# RUN DATABASE
# =========================================================

if __name__ == "__main__":

    create_database()