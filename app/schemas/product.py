from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ProductImageBase(BaseModel):
    image_url: str
    alt_text: Optional[str] = None
    display_order: int = 0
    is_primary: bool = False


class ProductImageCreate(ProductImageBase):
    pass


class ProductImageResponse(ProductImageBase):
    id: str
    product_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: str
    image_url: Optional[str] = None  # Keep for backward compatibility
    stock_quantity: int = 0
    

class ProductCreate(ProductBase):
    is_featured: bool = False
    is_new: bool = False
    images: Optional[List[ProductImageCreate]] = []  # New field for multiple images


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    stock_quantity: Optional[int] = None
    is_featured: Optional[bool] = None
    is_new: Optional[bool] = None
    images: Optional[List[ProductImageCreate]] = None  # Update images


class ProductResponse(ProductBase):
    id: str
    view_count: int
    order_count: int
    rating: float
    is_featured: bool
    is_new: bool
    created_at: datetime
    updated_at: datetime
    images: List[ProductImageResponse] = []  # Include images in response
    
    class Config:
        from_attributes = True


class ProductWithImages(ProductResponse):
    """Extended product response that ensures images are always populated"""
    pass