from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from pydantic import BaseModel
from app.core.database import get_db
from app.api.deps import get_current_active_user

router = APIRouter()

# Pydantic models for cart
class CartItemAdd(BaseModel):
    product_id: str
    quantity: int = 1


class CartItemUpdate(BaseModel):
    quantity: int


class CartItemResponse(BaseModel):
    product_id: str
    product_name: str
    price: float
    quantity: int
    image_url: Optional[str]
    stock_quantity: int
    subtotal: float


class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total: float
    item_count: int