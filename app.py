from router import route_message
from utils.agent_controller import agent_controller
from agents.receptionist import handle_receptionist
from agents.restaurant import handle_restaurant
from agents.room_service import handle_room_service
from db.database import create_tables
import re


def main():
    print("Welcome to PINK VILLA 🎀")
    print("How may I assist you today?")

    create_tables()

    guest_id = "guest"
    room_number = None
    pending_action = None
    pending_message = None

    while True:
        message = input("\nGuest: ")

        # ---------------- HANDLE PENDING ROOM NUMBER ----------------
        if pending_action:
            match = re.search(r"\d+", message)
            if match:
                room_number = match.group()
                action = pending_action
                original_message = pending_message

                pending_action = None
                pending_message = None

                if action == "restaurant":
                    response = handle_restaurant(original_message, room_number)
                    print("System:", response)
                    continue

                if action == "room_service":
                    response = handle_room_service(original_message, room_number)
                    print("System:", response)
                    continue

        # ---------------- EXIT ----------------
        if message.lower() in ["exit", "quit", "leaving"]:
            print("Thank you for visiting Pink Villa!")
            break

        # ---------------- ROUTING ----------------
        try:
            decision = agent_controller(message)
            department = decision.agent
        except Exception:
            
            department = route_message(message)

        # ---------------- AGENT EXECUTION ----------------
        if department == "receptionist":
            response = handle_receptionist(message, guest_id)

        elif department == "restaurant":
            if not room_number:
                pending_action = "restaurant"
                pending_message = message
                response = "Please provide your room number to place an order."
            else:
                response = handle_restaurant(message, room_number)

        elif department == "room_service":
            if not room_number:
                pending_action = "room_service"
                pending_message = message
                response = "Please provide your room number to request room service."
            else:
                response = handle_room_service(message, room_number)

        elif department == "checkout":
            if not room_number:
                response = "No active stay found. Please contact reception."
            else:
                from app import handle_checkout
                response = handle_checkout(room_number)
                print("System:", response)
                break

        else:
            response = "Sorry, I couldn't understand your request."

        print("System:", response)


if __name__ == "__main__":
    main()
