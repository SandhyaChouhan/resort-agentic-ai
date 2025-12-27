import pandas as pd
import re
from db.database import get_connection

MENU_FILE_PATH = "data/menu.xlsx"


def load_menu():
    """
    Load all menu items from Excel into a dictionary.
    Structure:
    {
        category: { item_name: price }
    }
    """
    menu = {}

    excel_file = pd.ExcelFile(MENU_FILE_PATH)

    for sheet_name in excel_file.sheet_names:
        df = excel_file.parse(sheet_name)

        # Normalize column names
        df.columns = (df.columns
                      .str.lower()
                      .str.lower()
        )
        for col in df.columns:
            if "price" in col:
                df = df.rename(columns={col:"price"})

        category = sheet_name.lower()
        menu[category] = {}

        for _, row in df.iterrows():
            item_name = str(row["item name"]).lower().strip()
            price = float(row["price"])

            menu[category][item_name] = price

    return menu


def handle_restaurant(message, room_number):
    """
    Handle food orders with quantity and itemized billing.
    Enforces strict menu checking.
    """

    menu = load_menu()
    message = message.lower()

    order_details = []  # [(item, qty, price)]
    total_amount = 0.0

    # Extract quantities like "2 poha", "1 upma"
    quantity_item_pairs = re.findall(r"(\d+)\s+([a-z\s]+)", message)

    matched_items = set()

    for qty, item_text in quantity_item_pairs:
        qty = int(qty)
        item_text = item_text.strip()

        for category, items in menu.items():
            for item_name, price in items.items():
                if item_name in item_text:
                    line_total = qty * price
                    order_details.append((item_name, qty, price, line_total))
                    total_amount += line_total
                    matched_items.add(item_name)

    # Handle items without explicit quantity (default = 1)
    for category, items in menu.items():
        for item_name, price in items.items():
            if item_name in message and item_name not in matched_items:
                order_details.append((item_name, 1, price, price))
                total_amount += price

    if not order_details:
        return " Sure! Please tell me what you’d like to order. We offer breakfast, Veg Starters, Non-Veg Starters, Veg main course, Non-Veg main course, Desserts, Drinks, and Breads."

    # Store order in DB
    conn = get_connection()
    cursor = conn.cursor()

    items_str = ", ".join(
        [f"{item} x{qty}" for item, qty, _, _ in order_details]
    )

    cursor.execute(
        """
        INSERT INTO restaurant_orders (room_number, items, total_amount, status)
        VALUES (?, ?, ?, ?)
        """,
        (room_number, items_str, total_amount, "Pending")
    )

    conn.commit()
    conn.close()

    # Build neat bill response
    response_lines = ["Order received, Please wait for sometime your food will reach to your room shortly!!!"]
    for item, qty, price, line_total in order_details:
        response_lines.append(
            f"- {item.title()} x{qty} → ₹{line_total}"
        )

    response_lines.append("-" * 20)
    response_lines.append(f"Total: ₹{total_amount}")

    return "\n".join(response_lines)

