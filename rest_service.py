from fastapi import FastAPI, HTTPException, status
from typing import List, Optional
import sys
import os

# Assuming db_manager.py and models.py are in the same directory
# We can safely import the CRUD functions
sys.path.append(os.path.dirname(__file__))
from db_manager import create_product, read_products, update_product, delete_product
from models import Product, ProductCreate, ProductUpdate

# --- 1. FastAPI App Initialization ---
app = FastAPI(
    title="Oracle Products REST API",
    description="A simple CRUD service for the Oracle PRODUCTS table using FastAPI and SQLAlchemy.",
    version="3.0"
)

# ===================================================================
# 2. REST ENDPOINTS (CRUD OPERATIONS)
# ===================================================================

# --- READ ALL / GET /products ---
@app.get("/products", response_model=List[Product], status_code=status.HTTP_200_OK, tags=["Products"])
def get_all_products():
    """
    Retrieve a list of all products from the database.
    """
    result = read_products() # Read ALL products (ID=None)
    
    if isinstance(result, str):
        # This is an error message from db_manager
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result)
        
    # The result is a list of tuples/rows, which Pydantic converts using response_model=List[Product]
    return result

# --- CREATE / POST /products ---
@app.post("/products", response_model=Product, status_code=status.HTTP_201_CREATED, tags=["Products"])
def create_new_product(product_data: ProductCreate):
    """
    Create a new product. ID must be unique.
    """
    # Call the core DB function
    result_message = create_product(
        product_data.id, 
        product_data.name, 
        product_data.quantity, 
        product_data.price
    )
    
    # Check the result message from db_manager
    if "[SUCCESS]" in result_message:
        # On success, read the product back to return the full object
        created_product = read_products(product_data.id)
        return created_product 
    
    # Handle errors (e.g., duplicate ID, validation failure from db_manager)
    if "[VALIDATION FAILED]" in result_message or "[ERROR]" in result_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=result_message.replace("[ERROR]", "").strip()
        )
    
    # Fallback error
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unknown error occurred during creation.")

# --- UPDATE / PUT /products/{id} ---
@app.put("/products/{product_id}", status_code=status.HTTP_200_OK, tags=["Products"])
def update_existing_product(product_id: int, product_data: ProductUpdate):
    """
    Update an existing product's quantity or price by ID.
    Only provided fields will be updated (partial update).
    """
    if not product_data.name and product_data.quantity is None and product_data.price is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Must provide at least one field (name, quantity, or price) to update.")

    result_message = update_product(
        product_id, 
        product_data.quantity,  # Note: Name update is not yet supported in db_manager.py update function
        product_data.price      
    )
    
    if "[SUCCESS]" in result_message:
        # Read and return the updated product for confirmation
        updated_product = read_products(product_id)
        if updated_product:
             return updated_product
        
    if "[VALIDATION FAILED]" in result_message or "[ERROR]" in result_message:
        # 404 for not found, 400 for bad data (e.g., negative value)
        status_code_map = {
            "not found": status.HTTP_404_NOT_FOUND,
            "negative": status.HTTP_400_BAD_REQUEST
        }
        status_code_to_use = status_code_map.get(
            result_message.lower().split(" ")[-1], # crude check for failure type
            status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(
            status_code=status_code_to_use, 
            detail=result_message.replace("[VALIDATION FAILED]", "").strip()
        )

# --- DELETE / DELETE /products/{id} ---
@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Products"])
def delete_existing_product(product_id: int):
    """
    Delete a product by ID.
    """
    result_message = delete_product(product_id)
    
    if "[SUCCESS]" in result_message:
        return # 204 No Content is ideal for successful deletion

    if "[VALIDATION FAILED]" in result_message:
        # Product not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=result_message.replace("[VALIDATION FAILED]", "").strip()
        )
        
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unknown error occurred during deletion.")


# ===================================================================
# 3. Connection and Startup Check
# ===================================================================

@app.on_event("startup")
def startup_event():
    """Verify database connection on startup."""
    try:
        # Attempt to read the system date to confirm connection
        connection_check = read_products(product_id=-1) # Use an invalid ID to just test the connection path
        if "[ERROR] Database Error" in str(connection_check):
             print(f"FATAL: Database connection failed during startup: {connection_check}")
             sys.exit(1)
        print("Database connection verified successfully on startup.")
    except Exception as e:
        print(f"FATAL: Could not verify database connection: {e}")
        sys.exit(1)