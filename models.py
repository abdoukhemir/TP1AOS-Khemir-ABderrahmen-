from pydantic import BaseModel, Field

# Define the model for creating and updating a product
class ProductBase(BaseModel):
    name: str = Field(..., max_length=100)
    # Ensure quantity is non-negative
    quantity: int = Field(..., ge=0, description="Stock quantity (must be non-negative)") 
    # Ensure price is non-negative
    price: float = Field(..., ge=0.0, description="Price (must be non-negative)")

# Model for incoming POST requests
class ProductCreate(ProductBase):
    # ID is required on creation via the API body
    id: int = Field(..., gt=0, description="Unique Product ID") 

# Model for PUT requests (all fields are optional for partial updates)
class ProductUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    quantity: int | None = Field(None, ge=0)
    price: float | None = Field(None, ge=0.0)

# Model for outgoing responses (matches the database schema)
class Product(ProductBase):
    id: int

    # Configuration for Pydantic
    class Config:
        from_attributes = True # Allows Pydantic to read ORM objects