def route_message(message):
    """
    Decide which department should handle the message.
    Returns one of: 'receptionist', 'restaurant', 'room_service'
    """

    message = message.lower()

    # Restaurant-related requests
    if any(word in message for word in ["order", "food", "menu", "eat"]):
        return "restaurant"

    # Room service-related requests
    elif any(word in message for word in ["clean", "laundry", "towel", "pillow", "blanket"
    ]):
        return "room_service"

    # Default: receptionist
    else:
        return "receptionist"
