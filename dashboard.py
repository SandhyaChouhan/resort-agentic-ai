import streamlit as st
import sqlite3
import pandas as pd

# ---------------- STYLING ----------------
st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #FAFAFA !important;
}
.main {
    background-color: #FAFAFA;
}
h1, h2, h3 {
    color: #E91E63 !important;
    font-family: 'Trebuchet MS', sans-serif;
}
[data-testid="metric-container"] {
    background-color: #FFE4EC;
    border-radius: 16px;
    padding: 15px;
    box-shadow: 2px 4px 10px rgba(0,0,0,0.08);
}
.stDataFrame {
    background-color: white;
    border-radius: 14px;
    padding: 10px;
    box-shadow: 1px 1px 6px rgba(0,0,0,0.08);
}
button {
    background-color: #E91E63 !important;
    color: white !important;
    border-radius: 12px !important;
    font-weight: bold;
}
hr {
    border: 1px solid #F8BBD0;
}
</style>
""", unsafe_allow_html=True)

# ---------------- DB ----------------
DB_PATH = "resort.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def status_badge(status):
    return {
        "Pending": "Pending",
        "In Progress": "In Progress",
        "Completed": "Completed",
        "Booked": "Booked",
        "Checked-in": "Occupied",
        "Checked-out": "Completed"
    }.get(status, status)

# ---------- UPDATE FUNCTIONS ----------
def update_restaurant_status(order_id, new_status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE restaurant_orders SET status=? WHERE order_id=?",
        (new_status, order_id)
    )
    conn.commit()
    conn.close()

def update_room_service_status(request_id, new_status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE room_service_requests SET status=? WHERE request_id=?",
        (new_status, request_id)
    )
    conn.commit()
    conn.close()

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Pink Villa Dashboard", layout="wide")
st.markdown("<h1>🎀 Pink Villa – Operations Dashboard 🎀</h1>", unsafe_allow_html=True)

conn = get_connection()

# ---------------- METRICS ----------------
total_rooms = pd.read_sql("SELECT COUNT(*) AS c FROM rooms", conn).iloc[0]["c"]

available_rooms = pd.read_sql("""
    SELECT COUNT(*) AS c FROM rooms
    WHERE room_number NOT IN (
        SELECT DISTINCT room_number
        FROM guest_stays
        WHERE status IN ('Booked','Checked-in')
    )
""", conn).iloc[0]["c"]

occupied_rooms = pd.read_sql("""
    SELECT COUNT(DISTINCT room_number) AS c
    FROM guest_stays
    WHERE status IN ('Booked','Checked-in')
""", conn).iloc[0]["c"]

checked_out = pd.read_sql("""
    SELECT COUNT(*) AS c
    FROM guest_stays WHERE status='Checked-out'
""", conn).iloc[0]["c"]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Rooms", total_rooms)
c2.metric("Available", available_rooms)
c3.metric("Booked", occupied_rooms)
c4.metric("Checked-out", checked_out)

st.divider()

# ---------------- ROOM INVENTORY ----------------
st.subheader("Room Inventory & Availability")

rooms_df = pd.read_sql("""
    SELECT r.room_number, r.floor, r.room_type, r.price_per_night,
           COALESCE(gs.status,'Available') AS status,
           gs.check_in, gs.expected_check_out
    FROM rooms r
    LEFT JOIN guest_stays gs
      ON r.room_number = gs.room_number
     AND gs.stay_id = (
        SELECT MAX(stay_id)
        FROM guest_stays
        WHERE room_number=r.room_number
          AND status IN ('Booked','Checked-in')
     )
    ORDER BY r.floor, r.room_number
""", conn)

rooms_df["status"] = rooms_df["status"].apply(status_badge)
st.dataframe(rooms_df, use_container_width=True)

st.divider()

# ---------------- RESTAURANT ORDERS ----------------
st.subheader("🍽 Restaurant Orders")

restaurant_df = pd.read_sql("""
    SELECT order_id, room_number, items, total_amount, status, timestamp
    FROM restaurant_orders
    ORDER BY timestamp DESC
""", conn)

if restaurant_df.empty:
    st.info("No restaurant orders yet.")
else:
    for _, row in restaurant_df.iterrows():
        c1, c2, c3, c4, c5, c6 = st.columns([1,1,3,1,1,2])

        c1.write(row["order_id"])
        c2.write(row["room_number"])
        c3.write(row["items"])
        c4.write(f"₹{row['total_amount']}")
        c5.markdown(f"**{status_badge(row['status'])}**")

        new_status = c6.selectbox(
            "Update",
            ["Pending","Completed"],
            index=["Pending","Completed"].index(row["status"]),
            key=f"rest_{row['order_id']}"
        )

        if c6.button("Save", key=f"rest_btn_{row['order_id']}"):
            update_restaurant_status(row["order_id"], new_status)
            st.rerun()

st.divider()

# ---------------- ROOM SERVICE ----------------
st.subheader("🧹 Room Service Requests")

room_service_df = pd.read_sql("""
    SELECT request_id, room_number, request_type, status, timestamp
    FROM room_service_requests
    ORDER BY timestamp DESC
""", conn)

if room_service_df.empty:
    st.info("No room service requests yet.")
else:
    for _, row in room_service_df.iterrows():
        c1, c2, c3, c4, c5 = st.columns([1,1,3,1,2])

        c1.write(row["request_id"])
        c2.write(row["room_number"])
        c3.write(row["request_type"])
        c4.markdown(f"**{status_badge(row['status'])}**")

        new_status = c5.selectbox(
            "Update",
            ["Pending","In Progress","Completed"],
            index=["Pending","In Progress","Completed"].index(row["status"]),
            key=f"room_{row['request_id']}"
        )

        if c5.button("Save", key=f"room_btn_{row['request_id']}"):
            update_room_service_status(row["request_id"], new_status)
            st.rerun()

st.divider()

# ---------------- GUEST STAYS ----------------
st.subheader("👩‍💼 Guest Stay Records")

guest_df = pd.read_sql("""
    SELECT stay_id, room_number, num_guests,
           check_in, expected_check_out, check_out, status
    FROM guest_stays
    ORDER BY stay_id DESC
""", conn)

guest_df["status"] = guest_df["status"].apply(status_badge)
st.dataframe(guest_df, use_container_width=True)

conn.close()
