"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: Optional[str] = Field(None, description="Address")
    phone: Optional[str] = Field(None, description="Phone number")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in currency units")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")
    image_url: Optional[str] = Field(None, description="Primary image URL")
    material: Optional[str] = Field(None, description="Material (e.g., gold, silver)")
    gemstones: Optional[List[str]] = Field(default=None, description="Gemstones used")

class OrderItem(BaseModel):
    product_id: str = Field(..., description="ID of the product")
    quantity: int = Field(1, ge=1, description="Quantity ordered")
    unit_price: float = Field(..., ge=0, description="Price per unit at time of order")
    title: str = Field(..., description="Product title snapshot")

class Order(BaseModel):
    """
    Orders collection schema
    Collection name: "order" (lowercase of class name)
    """
    customer_name: str = Field(..., description="Customer full name")
    customer_email: str = Field(..., description="Customer email")
    customer_phone: Optional[str] = Field(None, description="Customer phone")
    shipping_address: str = Field(..., description="Shipping address")
    items: List[OrderItem] = Field(..., description="List of items in the order")
    total_amount: float = Field(..., ge=0, description="Total order amount")
    notes: Optional[str] = Field(None, description="Additional notes")
