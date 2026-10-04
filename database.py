import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "food_orders.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            items TEXT NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'Pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    try:
        conn.execute("ALTER TABLE orders ADD COLUMN status TEXT DEFAULT 'Pending'")
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("ALTER TABLE orders ADD COLUMN address TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()


def save_order(customer_name, phone, address, cart, total_amount):
    items_text = ", ".join(f"{item_name} x{details['qty']}" for item_name, details in cart.items())
    conn = get_connection()
    conn.execute(
        "INSERT INTO orders (customer_name, phone, address, items, total_amount, status) VALUES (?, ?, ?, ?, ?, ?)",
        (customer_name.strip(), phone.strip(), address.strip(), items_text, float(total_amount), "Pending"),
    )
    conn.commit()
    conn.close()


def get_all_orders():
    conn = get_connection()
    orders = conn.execute(
        "SELECT id, customer_name, phone, address, items, total_amount, status, created_at FROM orders ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return orders


def update_order_status(order_id, status):
    conn = get_connection()
    conn.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    conn.commit()
    conn.close()


def delete_order(order_id):
    conn = get_connection()
    conn.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()
