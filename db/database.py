import sqlite3
from datetime import datetime, timedelta
from db.models import (
    create_rooms_table,
    create_restaurant_orders_table,
    create_room_service_table,
    create_guest_stay_table
)

DB_NAME = "resort.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    create_rooms_table(cursor)
    create_restaurant_orders_table(cursor)
    create_room_service_table(cursor)
    create_guest_stay_table(cursor)

    conn.commit()
    conn.close()

def seed_rooms():
    conn = get_connection()
    cursor = conn.cursor()
    rooms = []

    # Floor 2 - Normal rooms (201–205)
    for i in range(1, 6):
        room_no = 200 + i
        rooms.append((str(room_no), 2, "normal", 3000))

    # Floor 3 - Normal rooms (301–315)
    for i in range(1, 16):
        room_no = 300 + i
        rooms.append((str(room_no), 3, "normal", 3000))

    # Floor 4 - Normal rooms (401–407)
    for i in range(1, 8):
        room_no = 400 + i
        rooms.append((str(room_no), 4, "normal", 3000))

    # Floor 4 - Sea-facing rooms (408–415)
    for i in range(8, 16):
        room_no = 400 + i
        rooms.append((str(room_no), 4, "sea_facing", 5000))

    # Floor 5 - Normal rooms (501–507)
    for i in range(1, 8):
        room_no = 500 + i
        rooms.append((str(room_no), 5, "normal", 3000))

    # Floor 5 - Sea-facing rooms (508–515)
    for i in range(8, 16):
        room_no = 500 + i
        rooms.append((str(room_no), 5, "sea_facing", 5000))

    # Floor 6 - Penthouse
    rooms.append(("601", 6, "penthouse", 15000))
    rooms.append(("602", 6, "penthouse", 15000))

    for room in rooms:
        cursor.execute("""
            INSERT OR IGNORE INTO rooms
            (room_number, floor, room_type, price_per_night)
            VALUES (?, ?, ?, ?)
        """, room)

    conn.commit()
    conn.close()


def get_available_rooms(room_type, check_in_date, check_out_date):
    """
    Returns one available room_number for the given room_type
    and date range. Returns None if no room is available.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT room_number
        FROM rooms
        WHERE room_type = ?
        AND is_active = 1
        AND room_number NOT IN (
            SELECT room_number
            FROM guest_stays
            WHERE status IN ('Booked', 'Checked-in')
            AND NOT (
                expected_check_out <= ?
                OR check_in >= ?
            )
        )
        LIMIT 1
    """, (room_type, check_in_date, check_out_date))

    row = cursor.fetchone()
    conn.close()

    return row["room_number"] if row else None


def create_booking(room_type, check_in_date, nights, num_guests):
    """
    Create a room booking if availability exists.
    Returns room_number if booking is successful, else None.
    """

    # Calculate check-out date
    check_in = datetime.strptime(check_in_date, "%Y-%m-%d")
    expected_check_out = check_in + timedelta(days=nights)

    # Find available room
    room_number = get_available_rooms(
        room_type,
        check_in_date,
        expected_check_out.strftime("%Y-%m-%d")
    )

    if not room_number:
        return None

    # Insert booking
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO guest_stays
        (room_number, num_guests, check_in, expected_check_out, status)
        VALUES (?, ?, ?, ?, 'Booked')
    """, (
        room_number,
        num_guests,
        check_in_date,
        expected_check_out.strftime("%Y-%m-%d")
    ))

    conn.commit()
    conn.close()

    return room_number

