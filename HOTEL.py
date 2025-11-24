import sqlite3
from datetime import datetime
from prettytable import PrettyTable

DB_FILENAME = 'hotel8.db'

MENU_ITEMS = {
    "DOSA": 120, "IDLI": 100, "SAMOSA": 40, "PANI PURI": 50, "PIZZA": 300,
    "BURGER": 150, "FRIED RICE": 180, "NOODLES": 160, "PAV BHAJI": 90,
    "TEA": 20, "COFFEE": 40, "BIRYANI": 220, "THALI": 250, "SHAHI PANEER": 260,
    "TANDOORI ROTI": 30, "CHICKEN CURRY": 320, "FISH FRY": 350, "MUTTON": 400,
    "PANEER TIKKA": 180, "CHOWMEIN": 120, "SPRING ROLL": 80, "MILKSHAKE": 60,
    "ICE CREAM": 70, "FRUIT SALAD": 60, "VEG SOUP": 110
}

def display_vacant_rooms():
    with sqlite3.connect(DB_FILENAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT roomno FROM ROOMS WHERE status='vacant'")
        vacant = [row[0] for row in cur.fetchall()]
        print("Vacant rooms:", vacant if vacant else "No rooms available.")

def handle_checkin():
    display_vacant_rooms()
    room_num = input("Enter the room number for check-in: ")
    with sqlite3.connect(DB_FILENAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT status FROM ROOMS WHERE roomno=?", (room_num,))
        result = cur.fetchone()
        if not result:
            print("Sorry, that room doesn't exist.")
            return
        if result[0] == 'occupied':
            print("Room already booked.")
            return
        customer_name = input("Customer's full name: ")
        arrival = input("Check-in date (YYYY-MM-DD): ")
        departure = input("Check-out date (YYYY-MM-DD): ")
        cur.execute(
            "INSERT INTO CUSTOMERS (name, room_no, checkin_date, checkout_date) VALUES (?, ?, ?, ?)",
            (customer_name, room_num, arrival, departure)
        )
        cur.execute("UPDATE ROOMS SET status='occupied' WHERE roomno=?", (room_num,))
        conn.commit()
        print(f"{customer_name} has been checked in to room {room_num}.")

def place_food_order():
    room = input("Room number for food order: ")
    with sqlite3.connect(DB_FILENAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT status FROM ROOMS WHERE roomno=?", (room,))
        result = cur.fetchone()
        if not result or result[0] != 'occupied':
            print("That room isn't currently occupied.")
            return
        print("\n--- Available Menu ---")
        for dish, price in MENU_ITEMS.items():
            print(f"{dish:15} Rs.{price}")
        while True:
            selection = input("Type food item to order (or 'done' if finished): ").strip().upper()
            if selection == 'DONE':
                break
            if selection not in MENU_ITEMS:
                print("We don't have that item on our menu.")
                continue
            try:
                quantity = int(input(f"How many {selection}? "))
                if quantity <= 0:
                    print("Quantity must be more than zero.")
                    continue
            except ValueError:
                print("Please enter a valid number.")
                continue
            cur.execute(
                "INSERT INTO RESTAURANT (room_no, food_name, price, qty) VALUES (?, ?, ?, ?)",
                (room, selection, MENU_ITEMS[selection], quantity)
            )
            print(f"{quantity} x {selection} added to your order for room {room}.")
        conn.commit()

def process_checkout():
    customer = input("Name of the guest checking out: ")
    with sqlite3.connect(DB_FILENAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT room_no, checkin_date, checkout_date FROM CUSTOMERS WHERE name=?", (customer,))
        record = cur.fetchone()
        if not record:
            print("No customer by that name found.")
            return

        room_num, checkin, checkout = record
        try:
            duration = (datetime.strptime(checkout, "%Y-%m-%d") - datetime.strptime(checkin, "%Y-%m-%d")).days
            duration = max(1, duration)
        except Exception:
            duration = 1

        per_day = 10000
        total_room_cost = duration * per_day

        cur.execute("SELECT food_name, price, qty FROM RESTAURANT WHERE room_no=?", (room_num,))
        food_data = cur.fetchall()
        food_cost = sum(price * qty for _, price, qty in food_data)

        cust_table = PrettyTable(["Guest", "Room", "Check-in", "Check-out", "Nights Stayed"])
        cust_table.add_row([customer, room_num, checkin, checkout, duration])

        food_table = PrettyTable(["Item", "Rate (Rs)", "Qty", "Line Total (Rs)"])
        for f_name, f_price, f_qty in food_data:
            food_table.add_row([f_name, f_price, f_qty, f_price * f_qty])

        print("\n--- Guest Summary ---")
        print(cust_table)
        print("\n--- Food Charges ---")
        print(food_table)
        print(f"\nRoom cost: Rs. {total_room_cost}")
        print(f"Food cost: Rs. {food_cost}")
        print(f"Grand Total: Rs. {total_room_cost + food_cost}")

        cur.execute("DELETE FROM CUSTOMERS WHERE name=?", (customer,))
        cur.execute("DELETE FROM RESTAURANT WHERE room_no=?", (room_num,))
        cur.execute("UPDATE ROOMS SET status='vacant' WHERE roomno=?", (room_num,))
        conn.commit()
        print(f"Guest checked out. Room {room_num} marked as vacant.")

def start_hotel_system():
    while True:
        print("\nWelcome to the Hotel Desk")
        print("1. See available rooms")
        print("2. Guest check-in")
        print("3. Order food")
        print("4. Guest checkout")
        print("5. Quit")
        opt = input("Your option: ")
        if opt == '1':
            display_vacant_rooms()
        elif opt == '2':
            handle_checkin()
        elif opt == '3':
            place_food_order()
        elif opt == '4':
            process_checkout()
        elif opt == '5':
            print("Thank you. Visit again!")
            break
        else:
            print("That's not on the menu. Try again.")

if __name__ == "__main__":
    start_hotel_system()
