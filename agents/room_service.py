from db.database import get_connection


def handle_room_service(message, room_number):
    """
    Handle room service requests and store them in the database.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO room_service_requests (room_number, request_type, status)
        VALUES (?, ?, ?)
        """,
        (room_number, message, "Pending")
    )

    conn.commit()
    conn.close()

    return "Your room service request has been noted."


    