import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from decimal import Decimal

# Database configuration
config = {
    'user': 'root',
    'password': 'Rohit@1211',
    'host': '127.0.0.1',
    'database': 'GroceryStore'
}

# ===== Database Functions =====

def create_connection():
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            return connection
    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"Error connecting to database: {e}")
        return None

def close_connection(connection):
    if connection and connection.is_connected():
        connection.close()

def check_connection():
    conn = create_connection()
    if conn:
        messagebox.showinfo("Success", "Database connection established successfully")
        close_connection(conn)
    else:
        messagebox.showerror("Error", "Failed to establish database connection")

def reset_database():
    conn = create_connection()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute("DELETE FROM OrderDetails")
    cursor.execute("DELETE FROM Orders")
    cursor.execute("DELETE FROM Products")
    cursor.execute("DELETE FROM Customers")
    conn.commit()
    messagebox.showinfo("Success", "Database entries reset successfully")
    close_connection(conn)
    update_customer_dropdown()
    update_product_dropdown()

def add_customer():
    customer_name = customer_name_entry.get()
    if not customer_name:
        messagebox.showwarning("Input Error", "Customer name cannot be empty")
        return

    conn = create_connection()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Customers (CustomerName) VALUES (%s)", (customer_name,))
    conn.commit()
    messagebox.showinfo("Success", "Customer added successfully")
    close_connection(conn)
    customer_name_entry.delete(0, tk.END)
    update_customer_dropdown()

def add_product():
    product_name = product_name_entry.get()
    value_per_kg = value_per_kg_entry.get()
    if not product_name or not value_per_kg:
        messagebox.showwarning("Input Error", "Product name and value per kg cannot be empty")
        return

    try:
        value_per_kg = float(value_per_kg)
    except ValueError:
        messagebox.showwarning("Input Error", "Value per kg must be a number")
        return

    conn = create_connection()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Products (ProductName, ValuePerKg) VALUES (%s, %s)", (product_name, value_per_kg))
    conn.commit()
    messagebox.showinfo("Success", "Product added successfully")
    close_connection(conn)
    product_name_entry.delete(0, tk.END)
    value_per_kg_entry.delete(0, tk.END)
    update_product_dropdown()

def create_order():
    customer_value = customer_dropdown.get()
    if not customer_value:
        messagebox.showwarning("Input Error", "Please select a customer")
        return

    customer_id = customer_value.split(" - ")[0]  # Get the ID from "ID - Name"

    conn = create_connection()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Customers WHERE CustomerID = %s", (customer_id,))
    if cursor.fetchone() is None:
        messagebox.showerror("Error", f"No customer found with ID: {customer_id}")
        close_connection(conn)
        return

    cursor.execute("INSERT INTO Orders (CustomerID) VALUES (%s)", (customer_id,))
    conn.commit()
    order_id = cursor.lastrowid
    messagebox.showinfo("Success", f"Order created successfully with Order ID: {order_id}")
    close_connection(conn)

    order_id_entry.delete(0, tk.END)
    order_id_entry.insert(0, order_id)

def add_product_to_order():
    order_id = order_id_entry.get()
    product_name = product_dropdown.get()
    quantity_kg = quantity_kg_entry.get()

    if not order_id or not product_name or not quantity_kg:
        messagebox.showwarning("Input Error", "Order ID, Product Name, and Quantity cannot be empty")
        return

    try:
        quantity_kg = float(quantity_kg)
    except ValueError:
        messagebox.showwarning("Input Error", "Quantity must be a number")
        return

    conn = create_connection()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute("SELECT ProductID, ValuePerKg FROM Products WHERE ProductName = %s", (product_name,))
    product = cursor.fetchone()
    if not product:
        messagebox.showerror("Error", "Product not found")
        return

    product_id = product[0]
    value_per_kg = float(product[1])
    total_value = quantity_kg * value_per_kg

    cursor.execute("INSERT INTO OrderDetails (OrderID, ProductID, QuantityKg, TotalValue) VALUES (%s, %s, %s, %s)",
                   (order_id, product_id, quantity_kg, total_value))
    conn.commit()
    messagebox.showinfo("Success", f"Product added to order with total value: ${total_value:.2f}")
    total_value_label.config(text=f"Total Value: ${total_value:.2f}")
    close_connection(conn)
    quantity_kg_entry.delete(0, tk.END)

def update_product_dropdown():
    conn = create_connection()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute("SELECT ProductName FROM Products")
    products = cursor.fetchall()
    close_connection(conn)
    product_dropdown['values'] = [product[0] for product in products]

def update_customer_dropdown():
    conn = create_connection()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute("SELECT CustomerID, CustomerName FROM Customers")
    customers = cursor.fetchall()
    close_connection(conn)
    customer_dropdown['values'] = [f"{customer[0]} - {customer[1]}" for customer in customers]

# ===== GUI Setup =====

root = tk.Tk()
root.title("Grocery Store Management")
root.geometry("1024x768")

canvas = tk.Canvas(root, width=1024, height=768)
canvas.pack(fill="both", expand=True)

background_image = tk.PhotoImage(file="C:/Users/Rohit Raj/Desktop/grocery management/download 4.png")
canvas.create_image(0, 0, image=background_image, anchor="nw")

# Styling
style = {
    "label": {"bg": "#f0f4f7", "fg": "#333", "font": ("Segoe UI", 10, "bold")},
    "entry": {"font": ("Segoe UI", 10)},
    "button": {"bg": "#4caf50", "fg": "white", "font": ("Segoe UI", 10, "bold"), "relief": tk.RAISED, "bd": 2}
}

def styled_label(master, text):
    return tk.Label(master, text=text, **style["label"])

def styled_entry(master):
    return tk.Entry(master, **style["entry"])

def styled_button(master, text, command):
    return tk.Button(master, text=text, command=command, **style["button"])

def place_on_canvas(widget, x, y):
    canvas.create_window(x, y, window=widget, anchor="nw")

# === Customer Section ===
customer_frame = tk.Frame(canvas, bg="#f0f4f7")
place_on_canvas(customer_frame, 10, 10)

styled_label(customer_frame, "Customer Name:").pack(side=tk.LEFT, padx=5)
customer_name_entry = styled_entry(customer_frame)
customer_name_entry.pack(side=tk.LEFT, padx=5)
styled_button(customer_frame, "Add Customer", add_customer).pack(side=tk.LEFT, padx=5)

# === Product Section ===
product_frame = tk.Frame(canvas, bg="#f0f4f7")
place_on_canvas(product_frame, 10, 100)

styled_label(product_frame, "Product Name:").pack(side=tk.LEFT, padx=5)
product_name_entry = styled_entry(product_frame)
product_name_entry.pack(side=tk.LEFT, padx=5)

styled_label(product_frame, "Value per kg:").pack(side=tk.LEFT, padx=5)
value_per_kg_entry = styled_entry(product_frame)
value_per_kg_entry.pack(side=tk.LEFT, padx=5)

styled_button(product_frame, "Add Product", add_product).pack(side=tk.LEFT, padx=5)

# === Order Section ===
order_frame = tk.Frame(canvas, bg="#f0f4f7")
place_on_canvas(order_frame, 10, 200)

styled_label(order_frame, "Select Customer:").pack(side=tk.LEFT, padx=5)
customer_dropdown = ttk.Combobox(order_frame)
customer_dropdown.pack(side=tk.LEFT, padx=5)

styled_button(order_frame, "Create Order", create_order).pack(side=tk.LEFT, padx=5)

styled_label(order_frame, "Order ID:").pack(side=tk.LEFT, padx=5)
order_id_entry = styled_entry(order_frame)
order_id_entry.pack(side=tk.LEFT, padx=5)

styled_label(order_frame, "Product:").pack(side=tk.LEFT, padx=5)
product_dropdown = ttk.Combobox(order_frame)
product_dropdown.pack(side=tk.LEFT, padx=5)

styled_label(order_frame, "Quantity (kg):").pack(side=tk.LEFT, padx=5)
quantity_kg_entry = styled_entry(order_frame)
quantity_kg_entry.pack(side=tk.LEFT, padx=5)

styled_button(order_frame, "Add Product to Order", add_product_to_order).pack(side=tk.LEFT, padx=5)

total_value_label = tk.Label(order_frame, text="Total Value: $0.00", bg="#f0f4f7", fg="#00796b", font=("Segoe UI", 10, "bold"))
total_value_label.pack(side=tk.LEFT, padx=5)

# === Function Buttons ===
function_frame = tk.Frame(canvas, bg="#f0f4f7")
place_on_canvas(function_frame, 10, 450)

styled_button(function_frame, "Check Connection", check_connection).pack(side=tk.LEFT, padx=10)
styled_button(function_frame, "Reset Database", reset_database).pack(side=tk.LEFT, padx=10)

# Final setup
update_product_dropdown()
update_customer_dropdown()
root.mainloop()