import tkinter as tk
from tkinter import ttk, messagebox

from database import init_db, save_order, get_all_orders, delete_order, update_order_status

MENU_ITEMS = [
    {"name": "Margherita Pizza", "price": 180},
    {"name": "Veg Burger", "price": 120},
    {"name": "Chicken Burger", "price": 150},
    {"name": "Pasta Alfredo", "price": 200},
    {"name": "French Fries", "price": 90},
    {"name": "Cold Coffee", "price": 80},
    {"name": "Masala Dosa", "price": 110},
    {"name": "Spring Rolls", "price": 130},
    {"name": "Gobi Manchuria", "price": 80},
    {"name": "Paneer Khaju Rice", "price": 220},
    {"name": "Butter Naan", "price": 150},
    {"name": "Paneer Butter Masala", "price": 300},
    {"name": "Mushroom Biriyani", "price": 200},
    {"name": "Chicken Fried Rice", "price": 190},
    {"name": "Veg Biryani", "price": 170},
    {"name": "Mango Shake", "price": 100},
    {"name": "Crispy Corn", "price": 120},
]

COMBO_DEALS = [
    {"name": "Lunch Saver", "items": ["Veg Burger", "French Fries", "Cold Coffee"], "price": 260, "tag": "Save 12%"},
    {"name": "Pizza Party", "items": ["Margherita Pizza", "Spring Rolls", "Cold Coffee"], "price": 360, "tag": "Save 18%"},
    {"name": "Family Feast", "items": ["Paneer Butter Masala", "Mushroom Biriyani", "Butter Naan"], "price": 680, "tag": "Save 20%"},
]

REVIEWS = [
    "★★★★★ Fantastic taste and quick delivery!",
    "★★★★☆ Loved the combo deals and food quality.",
    "★★★★★ Best biriyani in town. Very fresh and tasty.",
    "★★★★☆ Affordable prices and friendly service.",
]




class FoodOrderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Food Order App")
        self.root.geometry("1100x820")
        self.root.minsize(1000, 760)
        self.root.configure(bg="#f4f4f4")

        self.cart = {}
        self.cart_names = []

        init_db()
        self.build_ui()
        self.update_cart()

    def build_ui(self):
        top_frame = tk.Frame(self.root, bg="#f4f4f4")
        top_frame.pack(fill="x", padx=20, pady=(20, 10))

        title = tk.Label(
            top_frame,
            text="Thanu's Restaurant",
            font=("Arial", 26, "bold"),
            fg="#7c2d12",
            bg="#fff7ed",
        )
        title.pack(side="left")

        offer_banner = tk.Label(
            top_frame,
            text="🔥 Free delivery above ₹399  •  50% OFF today",
            font=("Arial", 10, "bold"),
            fg="#fff",
            bg="#dc2626",
            padx=12,
            pady=6,
        )
        offer_banner.pack(side="right")

        self.status_label = tk.Label(
            top_frame,
            text="Welcome! Choose your food.",
            font=("Arial", 10),
            fg="#0f766e",
            bg="#fff7ed",
        )
        self.status_label.pack(side="right", padx=(0, 10))

        action_frame = tk.Frame(self.root, bg="#f4f4f4")
        action_frame.pack(fill="x", padx=20, pady=(0, 10))
        tk.Button(action_frame, text="Clear Cart", command=self.clear_cart, bg="#475569", fg="white", font=("Arial", 10, "bold"), padx=18, pady=8).pack(side="left")
        tk.Button(action_frame, text="Order History", command=self.show_order_history, bg="#7c3aed", fg="white", font=("Arial", 10, "bold"), padx=16, pady=8).pack(side="left", padx=10)
        tk.Button(action_frame, text="Admin Panel", command=self.show_admin_panel, bg="#0ea5e9", fg="white", font=("Arial", 10, "bold"), padx=16, pady=8).pack(side="left")

        combo_frame = tk.LabelFrame(self.root, text="Combo Deals", font=("Arial", 12, "bold"), bg="#fff7ed", fg="#78350f", padx=12, pady=8)
        combo_frame.pack(fill="x", padx=20, pady=(0, 12))

        for combo in COMBO_DEALS:
            combo_card = tk.Frame(combo_frame, bg="#fff", bd=1, relief="ridge", padx=10, pady=8, width=230, height=150)
            combo_card.pack(side="left", fill="y", padx=6, pady=2)
            combo_card.pack_propagate(False)

            tag_label = tk.Label(combo_card, text=combo["tag"], font=("Arial", 8, "bold"), bg="#fef3c7", fg="#92400e")
            tag_label.pack(anchor="w")

            combo_name = tk.Label(combo_card, text=combo["name"], font=("Arial", 10, "bold"), bg="#fff", fg="#111827")
            combo_name.pack(anchor="w", pady=(5, 2))

            items_text = ", ".join(combo["items"])
            combo_items = tk.Label(combo_card, text=items_text, font=("Arial", 8), bg="#fff", fg="#374151", justify="left", wraplength=170)
            combo_items.pack(anchor="w")

            combo_price = tk.Label(combo_card, text=f"₹{combo['price']}", font=("Arial", 10, "bold"), bg="#fff", fg="#059669")
            combo_price.pack(anchor="w", pady=(6, 0))

            add_btn = tk.Button(
                combo_card,
                text="Add to Cart",
                command=lambda c=combo: self.add_combo_to_cart(c),
                bg="#f97316",
                fg="white",
                font=("Arial", 8, "bold"),
                padx=10,
                pady=5,
            )
            add_btn.pack(side="bottom", anchor="e", pady=(8, 0))

        self.total_var = tk.StringVar(value="Grand Total: ₹0")
        checkout_bar = tk.Frame(self.root, bg="#7c2d12", padx=18, pady=10)
        checkout_bar.pack(side="bottom", fill="x", padx=20, pady=(0, 8))
        tk.Label(checkout_bar, textvariable=self.total_var, font=("Arial", 14, "bold"), bg="#7c2d12", fg="white").pack(side="left")
        tk.Button(checkout_bar, text="Place Order", command=self.place_order, bg="#16a34a", fg="white", font=("Arial", 11, "bold"), padx=24, pady=8).pack(side="right")

        main_frame = tk.Frame(self.root, bg="#fff7ed")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        left_panel = tk.LabelFrame(main_frame, text="Menu", font=("Arial", 13, "bold"), bg="#fffaf0", fg="#7c2d12", padx=15, pady=15)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 20))

        menu_canvas = tk.Canvas(left_panel, bg="#fffaf0", highlightthickness=0, width=560)
        menu_scroll = ttk.Scrollbar(left_panel, orient="vertical", command=menu_canvas.yview)
        menu_container = tk.Frame(menu_canvas, bg="#fffaf0")

        menu_canvas.configure(yscrollcommand=menu_scroll.set)
        menu_canvas.pack(side="left", fill="both", expand=True)
        menu_scroll.pack(side="right", fill="y")
        menu_canvas.create_window((0, 0), window=menu_container, anchor="nw")

        menu_title = tk.Label(menu_container, text=f"Menu Items ({len(MENU_ITEMS)} choices)", font=("Arial", 12, "bold"), bg="#fffaf0", fg="#7c2d12")
        menu_title.pack(anchor="w", pady=(0, 10))

        for item in MENU_ITEMS:
            card = tk.Frame(menu_container, bg="#fff", bd=1, relief="ridge", padx=18, pady=15, height=150)
            card.pack(fill="x", pady=8)
            card.pack_propagate(False)

            item_name = tk.Label(card, text=item["name"], font=("Arial", 12, "bold"), bg="#fff", fg="#111827")
            item_name.pack(anchor="w")

            item_price = tk.Label(card, text=f"₹{item['price']}", font=("Arial", 11, "bold"), bg="#fff", fg="#047857")
            item_price.pack(anchor="w", pady=(2, 0))

            tag_label = tk.Label(card, text="Popular" if item["price"] >= 150 else "Fresh", font=("Arial", 8, "bold"), bg="#fef3c7", fg="#92400e")
            tag_label.pack(anchor="w", pady=(6, 0))

            add_btn = tk.Button(
                card,
                text="Add to Cart",
                command=lambda menu_item=item: self.add_to_cart(menu_item),
                bg="#f97316",
                fg="white",
                font=("Arial", 9, "bold"),
                relief="flat",
                padx=14,
                pady=7,
            )
            add_btn.pack(side="bottom", anchor="e", pady=(10, 0))

        menu_container.update_idletasks()
        menu_canvas.config(scrollregion=menu_canvas.bbox("all"))

        right_panel = tk.LabelFrame(main_frame, text="Your Order", font=("Arial", 13, "bold"), bg="#fffaf0", fg="#7c2d12", padx=15, pady=15)
        right_panel.pack(side="right", fill="y")

        self.cart_list = tk.Listbox(right_panel, width=52, height=12, font=("Arial", 11), bg="#f9fafb", activestyle="none")
        self.cart_list.pack(fill="both", expand=True, pady=(0, 10))

        cart_buttons = tk.Frame(right_panel, bg="#ffffff")
        cart_buttons.pack(fill="x", pady=(0, 10))

        tk.Button(cart_buttons, text="Add Qty", command=self.increase_quantity, bg="#2563eb", fg="white", font=("Arial", 10, "bold"), padx=10).pack(side="left", expand=True, fill="x", padx=(0, 5))
        tk.Button(cart_buttons, text="Reduce Qty", command=self.decrease_quantity, bg="#f59e0b", fg="white", font=("Arial", 10, "bold"), padx=10).pack(side="left", expand=True, fill="x", padx=5)
        tk.Button(cart_buttons, text="Remove Item", command=self.remove_item, bg="#dc2626", fg="white", font=("Arial", 10, "bold"), padx=10).pack(side="left", expand=True, fill="x", padx=(5, 0))

        self.subtotal_var = tk.StringVar(value="Subtotal: ₹0")
        self.gst_var = tk.StringVar(value="GST: ₹0")
        self.delivery_var = tk.StringVar(value="Delivery: ₹0")
        self.item_count_var = tk.StringVar(value="Items: 0")

        subtotal_label = tk.Label(right_panel, textvariable=self.subtotal_var, font=("Arial", 10), bg="#ffffff", fg="#374151")
        subtotal_label.pack(anchor="w", pady=(5, 0))

        gst_label = tk.Label(right_panel, textvariable=self.gst_var, font=("Arial", 10), bg="#ffffff", fg="#374151")
        gst_label.pack(anchor="w")

        delivery_label = tk.Label(right_panel, textvariable=self.delivery_var, font=("Arial", 10), bg="#ffffff", fg="#374151")
        delivery_label.pack(anchor="w")

        total_label = tk.Label(right_panel, textvariable=self.total_var, font=("Arial", 14, "bold"), bg="#ffffff", fg="#111827")
        total_label.pack(anchor="w", pady=(5, 0))

        count_label = tk.Label(right_panel, textvariable=self.item_count_var, font=("Arial", 10), bg="#ffffff", fg="#374151")
        count_label.pack(anchor="w", pady=(0, 10))

        review_frame = tk.LabelFrame(self.root, text="Customer Reviews", font=("Arial", 12, "bold"), bg="#f0fdf4", fg="#166534", padx=15, pady=10)
        review_frame.pack(fill="x", padx=20, pady=(10, 20))

        reviews_box = tk.Listbox(review_frame, width=120, height=5, font=("Arial", 10), bg="#ffffff", activestyle="none")
        reviews_box.pack(fill="x")

        for review in REVIEWS:
            reviews_box.insert(tk.END, review)

    def add_combo_to_cart(self, combo):
        combo_name = combo["name"]
        combo_price = combo["price"]

        if combo_name in self.cart:
            self.cart[combo_name]["qty"] += 1
        else:
            self.cart[combo_name] = {"qty": 1, "price": combo_price}

        self.status_label.config(text=f"Added {combo_name} combo to cart")
        self.update_cart()

    def add_to_cart(self, item):
        name = item["name"]
        price = item["price"]

        if name in self.cart:
            self.cart[name]["qty"] += 1
        else:
            self.cart[name] = {"qty": 1, "price": price}

        self.status_label.config(text=f"Added {name} to cart")
        self.update_cart()

    def update_cart(self):
        self.cart_list.delete(0, tk.END)
        self.cart_names = list(self.cart.keys())

        subtotal = 0
        item_count = 0

        if not self.cart:
            self.cart_list.insert(tk.END, "Your cart is empty.")
            self.subtotal_var.set("Subtotal: ₹0")
            self.gst_var.set("GST: ₹0")
            self.delivery_var.set("Delivery: ₹0")
            self.total_var.set("Grand Total: ₹0")
            self.item_count_var.set("Items: 0")
            return

        for item_name, details in self.cart.items():
            qty = details["qty"]
            price = details["price"]
            line_total = qty * price
            subtotal += line_total
            item_count += qty
            self.cart_list.insert(tk.END, f"{item_name}  x{qty}  = ₹{line_total}")

        gst = round(subtotal * 0.05, 2)
        delivery = 0 if subtotal >= 399 else 40
        grand_total = subtotal + gst + delivery

        self.subtotal_var.set(f"Subtotal: ₹{subtotal}")
        self.gst_var.set(f"GST: ₹{gst}")
        self.delivery_var.set(f"Delivery: ₹{delivery}")
        self.total_var.set(f"Grand Total: ₹{grand_total}")
        self.item_count_var.set(f"Items: {item_count}")

        if subtotal >= 399:
            self.status_label.config(text="Free delivery unlocked! Your order qualifies for free delivery.")
        else:
            self.status_label.config(text="Add ₹%d more for free delivery." % (399 - subtotal))

    def get_selected_item_name(self):
        selected = self.cart_list.curselection()
        if not selected:
            return None
        index = selected[0]
        if not 0 <= index < len(self.cart_names):
            return None
        return self.cart_names[index]

    def increase_quantity(self):
        item_name = self.get_selected_item_name()
        if not item_name:
            messagebox.showwarning("Selection needed", "Please select an item from the cart.")
            return

        self.cart[item_name]["qty"] += 1
        self.status_label.config(text=f"Updated quantity for {item_name}")
        self.update_cart()

    def decrease_quantity(self):
        item_name = self.get_selected_item_name()
        if not item_name:
            messagebox.showwarning("Selection needed", "Please select an item from the cart.")
            return

        if self.cart[item_name]["qty"] <= 1:
            del self.cart[item_name]
        else:
            self.cart[item_name]["qty"] -= 1

        self.status_label.config(text=f"Updated quantity for {item_name}")
        self.update_cart()

    def remove_item(self):
        item_name = self.get_selected_item_name()
        if not item_name:
            messagebox.showwarning("Selection needed", "Please select an item from the cart.")
            return

        del self.cart[item_name]
        self.status_label.config(text=f"Removed {item_name} from cart")
        self.update_cart()

    def clear_cart(self):
        self.cart.clear()
        self.status_label.config(text="Cart cleared.")
        self.update_cart()

    def show_order_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("Order History")
        history_window.geometry("700x420")
        history_window.resizable(False, False)

        tk.Label(history_window, text="Recent Orders", font=("Arial", 16, "bold")).pack(pady=(15, 10))

        history_list = tk.Listbox(history_window, width=100, height=18, font=("Arial", 10))
        history_list.pack(padx=15, pady=(0, 10), fill="both", expand=True)

        orders = get_all_orders()
        if not orders:
            history_list.insert(tk.END, "No orders found yet.")
            return

        for order in orders:
            order_text = (
                f"Order #{order['id']} | {order['customer_name']} | {order['phone']} | "
                f"Status: {order['status']} | Items: {order['items']} | Total: ₹{order['total_amount']} | "
                f"Time: {order['created_at']}"
            )
            history_list.insert(tk.END, order_text)

    def show_admin_panel(self):
        admin_window = tk.Toplevel(self.root)
        admin_window.title("Admin Panel")
        admin_window.geometry("930x500")
        admin_window.resizable(False, False)

        tk.Label(admin_window, text="Order Management", font=("Arial", 18, "bold")).pack(pady=(15, 10))

        order_ids = []
        order_list = tk.Listbox(admin_window, width=120, height=18, font=("Arial", 10))
        order_list.pack(padx=15, fill="both", expand=True)

        controls = tk.Frame(admin_window, bg="#f4f4f4")
        controls.pack(fill="x", padx=15, pady=(0, 15))

        tk.Label(controls, text="Status:", font=("Arial", 11, "bold")).pack(side="left", padx=(0, 10))
        status_var = tk.StringVar(value="Pending")
        status_menu = ttk.Combobox(controls, textvariable=status_var, values=["Pending", "Preparing", "Ready", "Delivered"], width=18, state="readonly")
        status_menu.pack(side="left", padx=(0, 15))

        def refresh_orders():
            order_list.delete(0, tk.END)
            order_ids.clear()

            orders = get_all_orders()
            if not orders:
                order_list.insert(tk.END, "No orders found.")
                return

            for order in orders:
                order_ids.append(order["id"])
                summary = (
                    f"Order #{order['id']} | {order['customer_name']} | {order['phone']} | "
                    f"Status: {order['status']} | Total: ₹{order['total_amount']} | "
                    f"Items: {order['items']}"
                )
                order_list.insert(tk.END, summary)

        def update_selected_status():
            if not order_ids:
                messagebox.showwarning("No orders", "There are no orders to update.")
                return

            selected = order_list.curselection()
            if not selected:
                messagebox.showwarning("Selection needed", "Select an order first.")
                return

            order_id = order_ids[selected[0]]
            chosen_status = status_var.get()
            update_order_status(order_id, chosen_status)
            self.status_label.config(text=f"Order #{order_id} marked as {chosen_status}.")
            refresh_orders()

        def delete_selected_order():
            if not order_ids:
                messagebox.showwarning("No orders", "There are no orders to delete.")
                return

            selected = order_list.curselection()
            if not selected:
                messagebox.showwarning("Selection needed", "Select an order first.")
                return

            order_id = order_ids[selected[0]]
            delete_order(order_id)
            self.status_label.config(text=f"Order #{order_id} deleted.")
            refresh_orders()

        tk.Button(controls, text="Refresh", command=refresh_orders, bg="#2563eb", fg="white", font=("Arial", 10, "bold"), padx=12, pady=6).pack(side="left", padx=(0, 10))
        tk.Button(controls, text="Update Status", command=update_selected_status, bg="#16a34a", fg="white", font=("Arial", 10, "bold"), padx=12, pady=6).pack(side="left", padx=(0, 10))
        tk.Button(controls, text="Delete Selected", command=delete_selected_order, bg="#dc2626", fg="white", font=("Arial", 10, "bold"), padx=12, pady=6).pack(side="left")

        refresh_orders()

    def place_order(self):
        if not self.cart:
            messagebox.showwarning("Empty cart", "Please add at least one item before placing an order.")
            return

        order_window = tk.Toplevel(self.root)
        order_window.title("Place Order")
        order_window.geometry("420x380")
        order_window.resizable(False, False)

        tk.Label(order_window, text="Delivery Details", font=("Arial", 18, "bold")).pack(pady=(15, 12))
        tk.Label(order_window, text="Name", font=("Arial", 10)).pack(anchor="w", padx=20)
        name_entry = ttk.Entry(order_window, width=40)
        name_entry.pack(padx=20, pady=(0, 8), anchor="w")

        tk.Label(order_window, text="Phone Number", font=("Arial", 10)).pack(anchor="w", padx=20)
        phone_entry = ttk.Entry(order_window, width=40)
        phone_entry.pack(padx=20, pady=(0, 8), anchor="w")

        tk.Label(order_window, text="Address", font=("Arial", 10)).pack(anchor="w", padx=20)
        address_box = tk.Text(order_window, height=5, width=40)
        address_box.pack(padx=20, pady=(0, 12), anchor="w")

        def confirm_order():
            customer_name = name_entry.get().strip()
            phone = phone_entry.get().strip()
            address = address_box.get("1.0", "end").strip()

            if not customer_name or not phone or not address:
                messagebox.showwarning("Missing details", "Please enter your name, phone number, and address.", parent=order_window)
                return

            subtotal = sum(details["qty"] * details["price"] for details in self.cart.values())
            gst = round(subtotal * 0.05, 2)
            delivery = 0 if subtotal >= 399 else 40
            total = subtotal + gst + delivery
            save_order(customer_name, phone, address, self.cart, total)

            messagebox.showinfo(
                "Order placed",
                f"Thank you, {customer_name}! Your order has been placed.\nTotal bill: ₹{total}",
                parent=order_window,
            )
            order_window.destroy()
            self.cart.clear()
            self.status_label.config(text="Order placed successfully!")
            self.update_cart()

        tk.Button(order_window, text="Confirm Order", command=confirm_order, bg="#16a34a", fg="white", font=("Arial", 10, "bold"), padx=20, pady=8).pack()


if __name__ == "__main__":
    root = tk.Tk()
    app = FoodOrderApp(root)
    root.mainloop()
