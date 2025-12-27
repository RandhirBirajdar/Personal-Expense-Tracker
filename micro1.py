import csv
import os
import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from datetime import datetime


categories = ['Food', 'Rent', 'Transport', 'Shopping', 'Utilities', 'Health', 'Entertainment', 'Other']

def validate_date(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_amount(amount):
    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError
        return True
    except ValueError:
        return False

def is_duplicate(date, category, amount, description):
    if not os.path.exists('expenses.csv'):
        return False
    
    with open('expenses.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader, None)  
        for row in reader:
            if [date, category, str(amount), description] == row:
                return True
    return False

def add_expense(date_entry, category_var, amount_entry, description_entry, total_label):
    date = date_entry.get()
    category = category_var.get()
    amount = amount_entry.get()
    description = description_entry.get()

    if not validate_date(date):
        messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
        return
    
    if not validate_amount(amount):
        messagebox.showerror("Error", "Invalid amount. Please enter a positive number.")
        return

    if is_duplicate(date, category, amount, description):
        messagebox.showerror("Error", "Duplicate entry detected. Not added.")
        return

    file_exists = os.path.isfile('expenses.csv')
    
    with open('expenses.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Date', 'Category', 'Amount', 'Description'])
        writer.writerow([date, category, amount, description])

    messagebox.showinfo("Success", "Expense added successfully!")
    
    calculate_total_expenses(total_label)

    # Clear the text boxes after adding an expense
    date_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    description_entry.delete(0, tk.END)
    category_var.set(categories[0])  # Reset to the first category


def delete_selected_expense(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select an entry to delete.")
        return

    
    values = tree.item(selected_item, 'values')
    date, category, amount, description = values

    
    expenses = []
    with open('expenses.csv', 'r') as file:
        reader = csv.reader(file)
        header = next(reader)
        for row in reader:
            expenses.append(row)

    
    updated_expenses = [row for row in expenses if row != [date, category, amount, description]]

    
    with open('expenses.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)  
        writer.writerows(updated_expenses)

    
    tree.delete(selected_item)

    messagebox.showinfo("Success", "Expense deleted successfully!")

def view_expenses(total_label):
    if not os.path.exists('expenses.csv'):
        messagebox.showerror("Error", "No expenses found.")
        return

    top = tk.Toplevel()
    top.title("View Expenses")
    top.geometry("600x400")  
    top.transient()  
    top.grab_set()   

    tree = ttk.Treeview(top, columns=("Date", "Category", "Amount", "Description"), show='headings')
    tree.heading("Date", text="Date")
    tree.heading("Category", text="Category")
    tree.heading("Amount", text="Amount")
    tree.heading("Description", text="Description")

    tree.column("Date", width=100)
    tree.column("Category", width=100)
    tree.column("Amount", width=80)
    tree.column("Description", width=200)

    expenses = []
    with open('expenses.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader, None)  
        for row in reader:
            expenses.append(row)

    expenses.sort(key=lambda x: datetime.strptime(x[0], "%Y-%m-%d"))  # Sort by date

    for row in expenses:
        tree.insert('', tk.END, values=row)

    tree.pack(fill=tk.BOTH, expand=True)

    
    delete_button = tk.Button(top, text="Delete Selected Expense",
                              command=lambda: delete_selected_expense(tree, total_label),
                              bg="red", fg="white", font=("Arial", 12, "bold"))
    delete_button.pack(pady=10)

def generate_pie_chart():
    if not os.path.exists('expenses.csv'):
        messagebox.showerror("Error", "No expenses available to generate visualization.")
        return

    category_expenses = {cat: 0 for cat in categories}
    with open('expenses.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader, None)  
        for row in reader:
            category_expenses[row[1]] += float(row[2])

    
    filtered_expenses = {k: v for k, v in category_expenses.items() if v > 0}

    plt.figure(figsize=(8, 8))
    wedges, texts, autotexts = plt.pie(
        filtered_expenses.values(),
        labels=filtered_expenses.keys(),
        autopct='%1.1f%%',
        startangle=140,
        textprops={'fontsize': 10},
    )

    
    for text in texts:
        text.set_fontsize(10)
    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_color('black')

    plt.axis('equal')
    plt.title('Category-wise Spending')
    plt.tight_layout()
    plt.show()

def generate_bar_chart():
    if not os.path.exists('expenses.csv'):
        messagebox.showerror("Error", "No expenses available to generate visualization.")
        return

    monthly_expenses = {}
    with open('expenses.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader, None)  
        for row in reader:
            month = row[0][:7]  
            monthly_expenses[month] = monthly_expenses.get(month, 0) + float(row[2])

    
    sorted_months = sorted(monthly_expenses.keys(), key=lambda x: datetime.strptime(x, "%Y-%m"))

    plt.figure(figsize=(8, 6))
    plt.bar(sorted_months, [monthly_expenses[m] for m in sorted_months], color='skyblue')
    plt.xlabel('Month')
    plt.ylabel('Total Expenses (₹)')
    plt.title('Monthly Expenses')
    plt.xticks(rotation=45)
    plt.show()


def export_to_txt():
    if not os.path.exists('expenses.csv'):
        messagebox.showerror("Error", "No expenses available to export.")
        return

    with open('expenses.csv', 'r') as csv_file, open('expenses.txt', 'w') as txt_file:
        for line in csv_file:
            txt_file.write(line)
    messagebox.showinfo("Success", "Expenses exported to expenses.txt")

def search_expenses(search_entry):
    query = search_entry.get().strip().lower()
    if not query:
        messagebox.showerror("Error", "Enter a search term.")
        return

    if not os.path.exists('expenses.csv'):
        messagebox.showerror("Error", "No expenses found.")
        return

    results = []
    with open('expenses.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader, None)  
        for row in reader:
            if query in [item.lower() for item in row]:
                results.append(row)

    if not results:
        messagebox.showinfo("No Results", "No matching records found.")
        return

    top = tk.Toplevel()
    top.title("Search Results")

    tree = ttk.Treeview(top, columns=("Date", "Category", "Amount", "Description"), show='headings')
    tree.heading("Date", text="Date")
    tree.heading("Category", text="Category")
    tree.heading("Amount", text="Amount")
    tree.heading("Description", text="Description")

    for row in results:
        tree.insert('', tk.END, values=row)

    tree.pack(fill=tk.BOTH, expand=True)

def calculate_total_expenses(total_label):
    if not os.path.exists('expenses.csv'):
        total_label.config(text="Total Expenses: ₹0.00")
        return

    total = 0.0
    with open('expenses.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader, None)  
        for row in reader:
            total += float(row[2])

    total_label.config(text=f"Total Expenses: ₹{total:.2f}")


def delete_selected_expense(tree, total_label):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select an entry to delete.")
        return

    
    values = tree.item(selected_item, 'values')
    date, category, amount, description = values

    
    expenses = []
    with open('expenses.csv', 'r') as file:
        reader = csv.reader(file)
        header = next(reader)
        for row in reader:
            expenses.append(row)

    
    updated_expenses = [row for row in expenses if row != [date, category, amount, description]]

    
    with open('expenses.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)  
        writer.writerows(updated_expenses)

    
    tree.delete(selected_item)

    
    calculate_total_expenses(total_label)

    messagebox.showinfo("Success", "Expense deleted successfully!")

    

def main():
    root = tk.Tk()
    root.title("Personal Expense Tracker")
    root.geometry("500x550")  
    root.configure(bg="lightblue")

    frame = tk.Frame(root, bg="lightblue")
    frame.pack(expand=True)

    tk.Label(frame, text="Date (YYYY-MM-DD):", bg="lightblue", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky="ew")
    date_entry = tk.Entry(frame, font=("Arial", 12))
    date_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

    tk.Label(frame, text="Category:", bg="lightblue", font=("Arial", 12, "bold")).grid(row=1, column=0, padx=10, pady=5, sticky="ew")
    category_var = tk.StringVar(frame)
    category_var.set(categories[0])
    category_menu = ttk.Combobox(frame, textvariable=category_var, values=categories, font=("Arial", 12))
    category_menu.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

    tk.Label(frame, text="Amount (₹):", bg="lightblue", font=("Arial", 12, "bold")).grid(row=2, column=0, padx=10, pady=5, sticky="ew")
    amount_entry = tk.Entry(frame, font=("Arial", 12))
    amount_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

    tk.Label(frame, text="Description:", bg="lightblue", font=("Arial", 12, "bold")).grid(row=3, column=0, padx=10, pady=5, sticky="ew")
    description_entry = tk.Entry(frame, font=("Arial", 12))
    description_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

    button_style = {"font": ("Arial", 12, "bold"), "bg": "blue", "fg": "white", "padx": 10, "pady": 5}

    tk.Button(frame, text="Add Expense", command=lambda: add_expense(date_entry, category_var, amount_entry, description_entry, total_label), **button_style).grid(row=4, columnspan=2, pady=5)
    tk.Button(frame, text="View Expenses", command=lambda: view_expenses(total_label), **button_style).grid(row=5, columnspan=2, pady=5)
    tk.Button(frame, text="Generate Pie Chart", command=generate_pie_chart, **button_style).grid(row=6, columnspan=2, pady=5)
    tk.Button(frame, text="Generate Bar Chart", command=generate_bar_chart, **button_style).grid(row=7, columnspan=2, pady=5)
    tk.Button(frame, text="Export to TXT", command=export_to_txt, **button_style).grid(row=8, columnspan=2, pady=5)

    tk.Label(frame, text="Search:", bg="lightblue", font=("Arial", 12, "bold")).grid(row=9, column=0, padx=10, pady=5, sticky="ew")
    search_entry = tk.Entry(frame, font=("Arial", 12))
    search_entry.grid(row=9, column=1, padx=10, pady=5, sticky="ew")

    tk.Button(frame, text="Search", command=lambda: search_expenses(search_entry), **button_style).grid(row=10, columnspan=2, pady=5)

    
    total_label = tk.Label(root, text="Total Expenses: ₹0.00", bg="lightblue", font=("Arial", 14, "bold"))
    total_label.pack(pady=10)

    
    calculate_total_expenses(total_label)

    root.mainloop()


if __name__ == "__main__":
    main()
