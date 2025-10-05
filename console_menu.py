import os
import sys
# Import all CRUD functions from the database manager file
from db_manager import create_product, read_products, update_product, delete_product

# ===================================================================
# HELPER FUNCTIONS (Input and UI)
# ===================================================================

def clear_screen():
    # Clears the console
    os.system('cls' if os.name == 'nt' else 'clear')

def get_int_input(prompt, required=True):
    while True:
        try:
            value = input(prompt).strip()
            if not required and not value:
                return None
            return int(value)
        except ValueError:
            print("Invalid input. Please enter a whole number.")

def get_float_input(prompt, required=True):
    while True:
        try:
            value = input(prompt).strip()
            if not required and not value:
                return None
            return float(value)
        except ValueError:
            print("Invalid input. Please enter a number (e.g., 45.99).")

# ===================================================================
# MENU IMPLEMENTATIONS
# ===================================================================

def handle_create():
    print("\n--- CREATE PRODUCT ---")
    p_id = get_int_input("Enter Product ID: ")
    p_name = input("Enter Product Name: ").strip()
    p_qty = get_int_input("Enter Quantity: ")
    p_price = get_float_input("Enter Price: ")
    
    result = create_product(p_id, p_name, p_qty, p_price)
    print(f"\n{result}\n")

def handle_read():
    print("\n--- READ PRODUCTS ---")
    read_type = input("Read [A]ll or Read by [I]D? (A/I): ").upper()
    
    if read_type == 'A':
        results = read_products()
        
        print("\n" + "="*50)
        print(" " * 15 + "PRODUCTS LIST (ALL)".center(20))
        print("="*50)
        
        if isinstance(results, str): # Error or Info message from DB
             print(results)
        elif not results:
            print("No products found.")
        else:
            print(f"{'ID':<5}{'Name':<30}{'Qty':<5}{'Price':>10}")
            print("-" * 50)
            for row in results:
                print(f"{row[0]:<5}{row[1]:<30}{row[2]:<5}{row[3]:>10.2f}")
        print("="*50 + "\n")
        
    elif read_type == 'I':
        p_id = get_int_input("Enter Product ID to read: ")
        result = read_products(p_id)
        
        if isinstance(result, str): # Error or Info message
            print(f"\n{result}\n")
        else: # Found product
            print(f"\n--- Product Details (ID: {result[0]}) ---")
            print(f"Name: {result[1]}")
            print(f"Quantity: {result[2]}")
            print(f"Price: ${result[3]:.2f}\n")

def handle_update():
    print("\n--- UPDATE PRODUCT ---")
    p_id = get_int_input("Enter Product ID to update: ")
    
    print("Enter new values (leave blank to skip updating a field):")
    
    # Get values using the get_input functions with required=False
    new_qty = get_int_input("New Quantity: ", required=False)
    new_price = get_float_input("New Price: ", required=False)

    result = update_product(p_id, new_qty, new_price)
    print(f"\n{result}\n")

def handle_delete():
    print("\n--- DELETE PRODUCT ---")
    p_id = get_int_input("Enter Product ID to delete: ")
    
    result = delete_product(p_id)
    print(f"\n{result}\n")

def main_menu():
    while True:
        clear_screen()
        print("="*40)
        print(" ORACLE PRODUCTS CRUD CONSOLE ".center(40))
        print("="*40)
        print("1. Create Product (INSERT)")
        print("2. Read Products (SELECT)")
        print("3. Update Product (UPDATE)")
        print("4. Delete Product (DELETE)")
        print("5. Exit")
        print("="*40)

        choice = input("Enter your choice (1-5): ")

        try:
            if choice == '1':
                handle_create()
            elif choice == '2':
                handle_read()
            elif choice == '3':
                handle_update()
            elif choice == '4':
                handle_delete()
            elif choice == '5':
                print("Exiting console. Goodbye!")
                sys.exit(0)
            else:
                print("\nInvalid choice. Please enter a number between 1 and 5.")
                
            input("Press Enter to return to the menu...")
                
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")
            input("Press Enter to continue...")


if __name__ == "__main__":
    main_menu()