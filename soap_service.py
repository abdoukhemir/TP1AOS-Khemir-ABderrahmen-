import os
import sys
from spyne.application import Application
from spyne.decorator import srpc
from spyne.service import ServiceBase
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.model.primitive import Integer, String, Float, Unicode
from werkzeug.serving import run_simple

# Add the parent directory to the path so we can import db_manager.py
# Assuming db_manager.py is in the same directory
sys.path.append(os.path.dirname(__file__))
from db_manager import create_product, read_products, update_product, delete_product

# --- 1. Define the SOAP Service Class ---

class ProductService(ServiceBase):
    """
    Defines the SOAP methods that correspond to the CRUD operations 
    in your db_manager.py file.
    """
    
    # ---------------------------
    # CREATE Operation
    # srpc defines the SOAP method signature
    # (Input Types) -> [Return Type]
    # ---------------------------
    @srpc(Integer, Unicode, Integer, Float, _returns=Unicode)
    def createProduct(product_id, name, quantity, price):
        """Creates a new product and returns the status message."""
        # Call the existing function from db_manager.py
        return create_product(product_id, name, quantity, price)

    # ---------------------------
    # READ Operation (Get Single Product)
    # ---------------------------
    @srpc(Integer, _returns=Unicode)
    def getProduct(product_id):
        """Retrieves a single product by ID and returns its details as a formatted string."""
        result = read_products(product_id)
        
        if isinstance(result, str):
            # Return error/info messages directly
            return result
        
        if result:
            # Format the product tuple (id, name, quantity, price) into a string
            return (
                f"ID: {result[0]}, Name: {result[1]}, Quantity: {result[2]}, "
                f"Price: ${result[3]:.2f}"
            )
        return f"[INFO] Product with ID {product_id} not found."

    # ---------------------------
    # UPDATE Operation
    # Note: We use Float/Integer or None to handle optional updates (leaving blank)
    # ---------------------------
    @srpc(Integer, Integer.customize(min_occurs=0, nillable=True), Float.customize(min_occurs=0, nillable=True), _returns=Unicode)
    def updateProduct(product_id, new_quantity=None, new_price=None):
        """Updates the quantity and/or price of a product and returns the status."""
        
        # spyne passes None for optional fields if not provided.
        # We need to handle this conversion carefully.
        
        # Convert nillable=True fields to None if they are not provided
        qty_val = new_quantity if new_quantity is not None else None
        price_val = new_price if new_price is not None else None
        
        return update_product(product_id, qty_val, price_val)

    # ---------------------------
    # DELETE Operation
    # ---------------------------
    @srpc(Integer, _returns=Unicode)
    def deleteProduct(product_id):
        """Deletes a product by ID and returns the status message."""
        # Call the existing function from db_manager.py
        return delete_product(product_id)


# --- 2. Create Application and WSGI Server ---

# The namespace is used in the WSDL (e.g., targetNamespace)
APP_NAME = 'ProductServiceApp'
URL_PATH = 'product_service'
PORT = 8000

application = Application(
    [ProductService],
    tns=f'tns:{APP_NAME}',  # Target Namespace
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

wsgi_app = WsgiApplication(application)

# --- 3. Run the Server ---

if __name__ == '__main__':
    print(f"Starting SOAP server on http://127.0.0.1:{PORT}/{URL_PATH}?wsdl")
    print(f"WSDL URL: http://127.0.0.1:{PORT}/{URL_PATH}?wsdl")
    print("Use a tool like SoapUI or Postman to test the endpoints.")
    print("Press Ctrl+C to stop the server.")
    
    # Run the simple development server
    run_simple('127.0.0.1', PORT, wsgi_app)