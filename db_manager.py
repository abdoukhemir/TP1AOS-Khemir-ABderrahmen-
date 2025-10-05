from sqlalchemy import create_engine, text
import oracledb 
import sys

# --- 0. Connection Setup ---
INSTANT_CLIENT_PATH = r"C:\instantclient_21_19" # <-- USE YOUR CORRECT PATH
DB_USERNAME = "USERNAME"  
DB_PASSWORD = "123"       
DB_HOST = "localhost"     
DB_PORT = "1521"          
DB_SERVICE_NAME = "XE"    

# Initialize Instant Client (Thick Mode)
try:
    oracledb.init_oracle_client(lib_dir=INSTANT_CLIENT_PATH)
except Exception as e:
    print(f"FATAL ERROR: Could not initialize Instant Client. Error: {e}")
    sys.exit(1)

# SQLAlchemy Engine Setup
DB_URL = (
    f"oracle+oracledb://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/"
    f"?service_name={DB_SERVICE_NAME}"
)
engine = create_engine(DB_URL, echo=False)

# ===================================================================
# CRUD FUNCTIONS WITH VALIDATION
# ===================================================================

def _product_exists(product_id, connection):
    """Helper function to check if a product ID exists."""
    sql = text("SELECT 1 FROM products WHERE id = :id")
    result = connection.execute(sql, {"id": product_id}).fetchone()
    return result is not None

def create_product(product_id, name, quantity, price):
    """(C)reate: Inserts a new product into the table with validation."""
    
    # Validation for non-negative values
    if quantity < 0: return "[VALIDATION FAILED] Quantity must be non-negative."
    if price < 0: return "[VALIDATION FAILED] Price must be non-negative."
    
    try:
        with engine.connect() as connection:
            # Check for existing ID (Prevent Primary Key Error with a cleaner message)
            if _product_exists(product_id, connection):
                 return f"[ERROR] Product ID {product_id} already exists."
                 
            sql = text("""
                INSERT INTO products (id, name, quantity, price) 
                VALUES (:id, :name, :quantity, :price)
            """)
            connection.execute(sql, {"id": product_id, "name": name, "quantity": quantity, "price": price})
            connection.commit()
            return f"[SUCCESS] Product {product_id} ('{name}') inserted."
    except Exception as e:
        return f"[ERROR] Database Error: {e}"

def read_products(product_id=None):
    """(R)ead: Fetches product(s) from the table. Returns a list of dicts or a single dict."""
    try:
        with engine.connect() as connection:
            sql_text = "SELECT id, name, quantity, price FROM products"
            
            if product_id is None:
                sql = text(f"{sql_text} ORDER BY id")
                # When fetching all, we want rows that can be converted to dicts
                result = connection.execute(sql).mappings().all() 
                return list(result)
            else:
                sql = text(f"{sql_text} WHERE id = :id")
                # When fetching one, we want a single row converted to a dict
                result = connection.execute(sql, {"id": product_id}).mappings().one_or_none()
                if result:
                    # Convert the MappedRow to a standard dict for FastAPI/Pydantic
                    return dict(result) 
                return f"[INFO] Product with ID {product_id} not found."
    except Exception as e:
        return f"[ERROR] Database Error: {e}"

def update_product(product_id, new_quantity=None, new_price=None):
    """(U)pdate: Modifies quantity and/or price of a product with ID/value validation."""
    
    # Validation for non-negative values in update fields
    if new_quantity is not None and new_quantity < 0: 
        return "[VALIDATION FAILED] New Quantity must be non-negative."
    if new_price is not None and new_price < 0:
        return "[VALIDATION FAILED] New Price must be non-negative."

    updates = []
    params = {"id": product_id}

    if new_quantity is not None:
        updates.append("quantity = :quantity")
        params["quantity"] = new_quantity
    if new_price is not None:
        updates.append("price = :price")
        params["price"] = new_price

    if not updates:
        return "[INFO] No update values provided."

    try:
        with engine.connect() as connection:
            # 1. Validate Product ID existence BEFORE attempting update
            if not _product_exists(product_id, connection):
                return f"[VALIDATION FAILED] Cannot update: Product ID {product_id} not found."

            # 2. Execute Update
            sql = text(f"UPDATE products SET {', '.join(updates)} WHERE id = :id")
            result = connection.execute(sql, params)
            connection.commit()
            
            # Note: Because we checked existence above, rowcount should be > 0 here.
            return f"[SUCCESS] Product {product_id} updated."
    except Exception as e:
        return f"[ERROR] Database Error: {e}"

def delete_product(product_id):
    """(D)elete: Removes a product from the table with ID validation."""
    try:
        with engine.connect() as connection:
            # 1. Validate Product ID existence BEFORE attempting delete
            if not _product_exists(product_id, connection):
                return f"[VALIDATION FAILED] Cannot delete: Product ID {product_id} not found."

            # 2. Execute Delete
            sql = text("DELETE FROM products WHERE id = :id")
            result = connection.execute(sql, {"id": product_id})
            connection.commit()
            
            # Note: Because we checked existence above, rowcount should be > 0 here.
            return f"[SUCCESS] Product {product_id} deleted."
    except Exception as e:
        return f"[ERROR] Database Error: {e}"