# db/models.py

def create_restaurant_orders_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS restaurant_orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT,
            items TEXT,
            total_amount REAL,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)


def create_room_service_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS room_service_requests (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT,
            request_type TEXT,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)


def create_guest_stay_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS guest_stays (
            stay_id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT NOT NULL,
            num_guests INTEGER CHECK(num_guests <= 2),
            check_in DATE,
            expected_check_out DATE,
            check_out TIMESTAMP,
            status TEXT DEFAULT 'Checked-in'
        )
    """)
def create_rooms_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            room_number TEXT PRIMARY KEY,
            floor INTEGER,
            room_type TEXT,
            price_per_night INTEGER,
            is_active INTEGER DEFAULT 1
        )
    """)
