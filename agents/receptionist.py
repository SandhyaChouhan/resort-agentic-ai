from db.database import create_booking

# -------------------------------
# In-memory booking conversation state
# -------------------------------
booking_state = {}


def handle_booking_flow(message, guest_id):
    """
    Handles guided room booking conversation.
    """
    state = booking_state.get(guest_id)

    # STEP 0: Start booking
    if not state:
        booking_state[guest_id] = {"step": "room_type"}
        return (
            "Sure, Which room would you prefer?\n"
            "1️. Normal room\n"
            "2️. Sea-facing balcony room"
        )

    step = state["step"]
    message = message.lower()

    # STEP 1: Room type
    if step == "room_type":
        if "sea" in message:
            state["room_type"] = "sea_facing"
        elif "normal" in message:
            state["room_type"] = "normal"
        else:
            return "Please choose either **Normal** or **Sea-facing** room."

        state["step"] = "num_guests"
        return "How many guests will be staying? (Max 2)"

    # STEP 2: Number of guests
    if step == "num_guests":
        try:
            guests = int(message)
            if guests < 1 or guests > 2:
                raise ValueError
            state["num_guests"] = guests
        except ValueError:
            return "Please enter a valid number (1 or 2)."

        state["step"] = "check_in"
        return "What is your check-in date? (YYYY-MM-DD)"

    # STEP 3: Check-in date
    if step == "check_in":
        state["check_in"] = message
        state["step"] = "nights"
        return "How many nights will you be staying?"

    # STEP 4: Nights & booking confirmation
    if step == "nights":
        try:
            nights = int(message)
            if nights < 1:
                raise ValueError
            state["nights"] = nights
        except ValueError:
            return "Please enter a valid number of nights."

        room = create_booking(
            state["room_type"],
            state["check_in"],
            state["nights"],
            state["num_guests"]
        )

        # Clear state after attempt
        del booking_state[guest_id]

        if not room:
            return "Sorry, No rooms are available for the selected dates."

        return (
            f"Your room has been reserved successfully!\n"
            f"Room Number: {room}\n"
            f"Please complete payment at reception to confirm your booking."
        )


def handle_receptionist(message, guest_id="guest"):
    """
    Handle receptionist queries + booking flow.
    """
    message_lower = message.lower()
    responses = []

    # -------------------------------
    # Booking intent (PRIORITY)
    # -------------------------------
    if "book" in message_lower or guest_id in booking_state:
        return handle_booking_flow(message, guest_id)

    # -------------------------------
    # General FAQs
    # -------------------------------
    if "check-in" in message_lower:
        responses.append(" Check-in time is 2:00 PM.")

    if "check-out" in message_lower:
        responses.append("Check-out time is 11:00 AM.")

    if "gym" in message_lower:
        responses.append("The gym is open from 6:00 AM to 10:00 PM.")

    if "pool" in message_lower:
        responses.append("The swimming pool is open from 7:00 AM to 9:00 PM.")

    if "spa" in message_lower:
        responses.append(" The spa is open from 9:00 AM to 8:00 PM.")

    if "thank" in message_lower:
        responses.append("You're welcome! Enjoy your stay at Pink Villa.")

    if "leaving" in message_lower:
        responses.append("Thank you for staying with us. Have a safe journey!")

    # -------------------------------
    # Default response
    # -------------------------------
    if not responses:
        return "Receptionist: How may I assist you today?"

    return " ".join(responses)
