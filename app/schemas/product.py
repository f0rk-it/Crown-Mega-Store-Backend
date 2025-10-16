from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    category: str
    image_url: Optional[str] = None
    stock_quantity: int = 0
    

class ProductCreate(ProductBase):
    is_featured: bool = False
    is_new: bool = False


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    stock_quantity: Optional[int] = None
    is_featured: Optional[bool] = None
    is_new: Optional[bool] = None


class ProductResponse(ProductBase):
    id: str
    view_count: int
    order_count: int
    rating: Decimal
    is_featured: bool
    is_new: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True