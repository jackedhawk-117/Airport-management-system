import mysql.connector
from tkinter import *
from tkinter import messagebox, ttk

# Function to connect to the database
def connect_to_database():
    global admin_db, admin_cursor
    admin_db = mysql.connector.connect(
        host="localhost",
        user="ADMIN",
        password="CharlieTango-65",
        database="AIRPORT"
    )
    admin_cursor = admin_db.cursor()

# Function to fetch and display data from a specified table in a new window
def fetch_table_data(table_name):
    def load_data():
        # Clear the treeview
        for row in tree.get_children():
            tree.delete(row)
        
        # Fetch data from the database
        admin_cursor.execute(f"SELECT * FROM {table_name}")
        records = admin_cursor.fetchall()

        # Insert records into the treeview
        for row in records:
            tree.insert("", END, values=row)

    # Create a new window for the table
    table_window = Toplevel(root)
    table_window.title(f"{table_name} Data")
    table_window.geometry("800x400")

    # Create a Treeview to display the data
    columns = get_table_columns(table_name)
    tree = ttk.Treeview(table_window, columns=columns, show='headings')
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor='center')
    tree.pack(expand=True, fill='both')

    # Load initial data
    load_data()

    # Buttons to insert, edit, and delete records
    Button(table_window, text="Insert Record", command=lambda: insert_record(table_name)).pack(side=LEFT, padx=10, pady=10)
    Button(table_window, text="Edit Selected Record", command=lambda: edit_record(table_name, tree)).pack(side=LEFT, padx=10, pady=10)
    Button(table_window, text="Delete Selected Record", command=lambda: delete_record(table_name, tree)).pack(side=LEFT, padx=10, pady=10)

# Function to get table columns
def get_table_columns(table_name):
    admin_cursor.execute(f"SHOW COLUMNS FROM {table_name}")
    return [column[0] for column in admin_cursor.fetchall()]

# Function to insert a new record into the specified table
def insert_record(table_name):
    def submit_record():
        values = [entry.get() for entry in entries]
        if all(values):  # Ensure all fields are filled
            query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(values))})"
            try:
                admin_cursor.execute(query, values)
                admin_db.commit()
                messagebox.showinfo("Success", "Record inserted successfully!")
                insert_window.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Error: {err}")
        else:
            messagebox.showwarning("Input Error", "Please fill all fields.")

    insert_window = Toplevel(root)
    insert_window.title(f"Insert into {table_name}")
    columns = get_table_columns(table_name)

    entries = []
    for column in columns:
        Label(insert_window, text=column).pack(pady=5)
        entry = Entry(insert_window)
        entry.pack(pady=5)
        entries.append(entry)

    Button(insert_window, text="Submit", command=submit_record).pack(pady=10)

# Function to delete a selected record
def delete_record(table_name, tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Warning", "Please select a record to delete.")
        return

    record = tree.item(selected_item)['values']
    record_id = record[0]  # Assuming the first element is the ID

    admin_cursor.execute(f"DELETE FROM {table_name} WHERE id = %s", (record_id,))
    admin_db.commit()
    messagebox.showinfo("Success", "Record deleted successfully!")
    fetch_table_data(table_name)  # Refresh the treeview

# Function to edit a selected record
def edit_record(table_name, tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Warning", "Please select a record to edit.")
        return

    record = tree.item(selected_item)['values']
    record_id = record[0]  # Assuming the first element is the ID

    edit_window = Toplevel(root)
    edit_window.title(f"Edit {table_name} Record")

    columns = get_table_columns(table_name)
    entries = []
    for i, column in enumerate(columns):
        Label(edit_window, text=column).pack(pady=5)
        entry = Entry(edit_window)
        entry.pack(pady=5)
        entry.insert(0, record[i])  # Fill in the existing record data
        entries.append(entry)

    def submit_edit():
        values = [entry.get() for entry in entries]
        if all(values):  # Ensure all fields are filled
            query = f"UPDATE {table_name} SET {', '.join([f'{col}=%s' for col in columns[1:]])} WHERE id = %s"
            try:
                admin_cursor.execute(query, values[1:] + [record_id])
                admin_db.commit()
                messagebox.showinfo("Success", "Record updated successfully!")
                edit_window.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Error: {err}")
        else:
            messagebox.showwarning("Input Error", "Please fill all fields.")

    Button(edit_window, text="Submit", command=submit_edit).pack(pady=10)

# Function to check admin credentials
def check_admin_credentials():
    username = entry_username.get()
    password = entry_password.get()

    if username == "ADMIN" and password == "CharlieTango-65":
        messagebox.showinfo("Success", "Admin logged in successfully!")
        login_frame.pack_forget()  # Hide login frame
        main_app_frame.pack()  # Show main app frame
        connect_to_database()  # Connect to the database
    else:
        messagebox.showerror("Error", "Invalid credentials. Please try again.")

# Function for customers to book tickets
def book_ticket():
    customer_name = entry_name.get()
    flight_id = entry_flight_id.get()
    seat_class = entry_seat_class.get()

    if not customer_name or not flight_id or not seat_class:
        messagebox.showwarning("Input Error", "Please fill all fields.")
        return

    # Insert booking into Tickets table
    query = "INSERT INTO Tickets (customer_name, flight_id, seat_class) VALUES (%s, %s, %s)"
    try:
        admin_cursor.execute(query, (customer_name, flight_id, seat_class))
        admin_db.commit()
        messagebox.showinfo("Success", "Ticket booked successfully!")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error: {err}")

# Function for registering a new customer
def register_customer():
    new_customer_name = entry_new_customer_name.get()
    new_customer_password = entry_new_customer_password.get()

    if not new_customer_name or not new_customer_password:
        messagebox.showwarning("Input Error", "Please fill all fields.")
        return

    # Insert new customer into Customers table
    query = "INSERT INTO Customers (username, password) VALUES (%s, %s)"
    try:
        admin_cursor.execute(query, (new_customer_name, new_customer_password))
        admin_db.commit()
        messagebox.showinfo("Success", "Customer registered successfully!")
        entry_new_customer_name.delete(0, END)
        entry_new_customer_password.delete(0, END)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error: {err}")

# Tkinter window
root = Tk()
root.title("Airport Management System")
root.geometry("800x800")  # Increased window size

# Login Frame
login_frame = Frame(root)
login_frame.pack(pady=20)

Label(login_frame, text="Username:").grid(row=0, column=0)
entry_username = Entry(login_frame)
entry_username.grid(row=0, column=1)

Label(login_frame, text="Password:").grid(row=1, column=0)
entry_password = Entry(login_frame, show='*')
entry_password.grid(row=1, column=1)

Button(login_frame, text="Login", command=check_admin_credentials).grid(row=2, columnspan=2)

# Main App Frame (initially hidden)
main_app_frame = Frame(root)

# Labels for showing available tables
Label(main_app_frame, text="Admin Panel").pack(pady=10)

# Buttons to fetch data from each table
tables = ["Aircraft", "Customers", "Employees", "Flights", "Passengers", "Tickets"]
for table in tables:
    Button(main_app_frame, text=f"View {table}", command=lambda t=table: fetch_table_data(t)).pack(pady=5)

# Start the application
root.mainloop()

