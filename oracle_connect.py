from sqlalchemy import create_engine, text
import oracledb 

# --- 0. Instant Client Setup (Keep this!) ---
INSTANT_CLIENT_PATH = r"C:\instantclient_21_19" # <-- Use your correct path

try:
    oracledb.init_oracle_client(lib_dir=INSTANT_CLIENT_PATH)
    print("Oracle Thick Client (Instant Client) initialized successfully.")
except Exception as e:
    print(f"FATAL ERROR: Could not initialize Instant Client. Check the path: {INSTANT_CLIENT_PATH}. Error: {e}")
    exit(1)
# -------------------------------------------------------------------


# --- 1. Define Your Connection Details ---
DB_USERNAME = "USERNAME"  
DB_PASSWORD = "123"       
DB_HOST = "localhost"     
DB_PORT = "1521"          
DB_SERVICE_NAME = "XE"    

DB_URL = (
    f"oracle+oracledb://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/"
    f"?service_name={DB_SERVICE_NAME}"
)

engine = create_engine(DB_URL, echo=False)

# ===================================================================
# CRUD FUNCTIONS
# ===================================================================

def create_product(product_id, name, quantity, price):
    """(C)reate: Inserts a new product into the table with validation."""
    
    # --- Input Validation ---
    if quantity < 0:
        print(f"[VALIDATION FAILED] Cannot create product '{name}'. Quantity must be non-negative (Received: {quantity}).")
        return # Stop execution of this function
    
    if price < 0:
        print(f"[VALIDATION FAILED] Cannot create product '{name}'. Price must be non-negative (Received: {price}).")
        return # Stop execution of this function
    # ------------------------
    
    try:
        with engine.connect() as connection:
            sql = text("""
                INSERT INTO products (id, name, quantity, price) 
                VALUES (:id, :name, :quantity, :price)
            """)
            connection.execute(sql, {"id": product_id, "name": name, "quantity": quantity, "price": price})
            connection.commit()
            print(f"[CREATE] Product {product_id} ({name}) inserted successfully.")
    except Exception as e:
        print(f"[CREATE] Error inserting product: {e}")

# (The rest of the CRUD functions: read_products, update_product_price, and delete_product remain the same)

def read_products(product_id=None):
    """(R)ead: Fetches product(s) from the table."""
    try:
        with engine.connect() as connection:
            if product_id is None:
                # Read ALL products
                sql = text("SELECT id, name, quantity, price FROM products ORDER BY id")
                result = connection.execute(sql)
                
                print("\n--- ALL PRODUCTS ---")
                for row in result:
                    print(f"ID: {row[0]}, Name: {row[1]}, Qty: {row[2]}, Price: ${row[3]:.2f}")
                print("--------------------\n")
            else:
                # Read a single product
                sql = text("SELECT id, name, quantity, price FROM products WHERE id = :id")
                result = connection.execute(sql, {"id": product_id}).fetchone()
                
                if result:
                    print(f"\n--- READ Product {product_id} ---")
                    print(f"ID: {result[0]}, Name: {result[1]}, Qty: {result[2]}, Price: ${result[3]:.2f}")
                    print("-------------------------\n")
                else:
                    print(f"\nProduct with ID {product_id} not found.\n")
    except Exception as e:
        print(f"[READ] Error reading products: {e}")

def update_product_price(product_id, new_price):
    """(U)pdate: Modifies the price of an existing product."""
    # Note: You should ideally also validate updates, but keeping this simple for now.
    try:
        with engine.connect() as connection:
            sql = text("UPDATE products SET price = :price WHERE id = :id")
            result = connection.execute(sql, {"price": new_price, "id": product_id})
            connection.commit()
            
            if result.rowcount > 0:
                print(f"[UPDATE] Product {product_id} price updated to ${new_price:.2f}.")
            else:
                print(f"[UPDATE] Product {product_id} not found.")
    except Exception as e:
        print(f"[UPDATE] Error updating product: {e}")

def delete_product(product_id):
    """(D)elete: Removes a product from the table."""
    try:
        with engine.connect() as connection:
            sql = text("DELETE FROM products WHERE id = :id")
            result = connection.execute(sql, {"id": product_id})
            connection.commit()
            
            if result.rowcount > 0:
                print(f"[DELETE] Product {product_id} deleted successfully.")
            else:
                print(f"[DELETE] Product {product_id} not found.")
    except Exception as e:
        print(f"[DELETE] Error deleting product: {e}")


# ===================================================================
# EXECUTION (Demonstrates CRUD operations including validation test)
# ===================================================================

if __name__ == "__main__":
    print("\nStarting CRUD demonstration with validation...\n")

    # 1. CREATE Operations (Insert 2 valid rows)
    create_product(1, "Laptop Bag", 100, 45.99)
    create_product(2, "Wireless Mouse", 500, 19.99)
    
    # 2. VALIDATION TEST: Attempt to insert a product with negative quantity
    create_product(4, "Invalid Qty Item", -10, 50.00)
    
    # 3. VALIDATION TEST: Attempt to insert a product with negative price
    create_product(5, "Invalid Price Item", 10, -5.00)

    # 4. READ Operation (Only the first two should have been created)
    read_products()

    # 5. UPDATE Operation 
    update_product_price(2, 24.99)

    # 6. DELETE Operation 
    delete_product(1)
    
    print("CRUD demonstration complete.")