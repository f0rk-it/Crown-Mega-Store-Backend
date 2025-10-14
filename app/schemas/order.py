from pydantic import BaseModel, EmailStr
from typing import List, Optional, Literal
from datetime import datetime
from decimal import Decimal


class OrderItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    price: Decimal


class CustomerInfo(BaseModel):
    name: str
    email: EmailStr
    phone: str
    delivery_address: Optional[str] = None
    pickup_preference: bool = False
    order_notes: Optional[str] = None
    payment_preference: str = 'bank_transfer'


class OrderCreate(BaseModel):
    items: List[OrderItem]
    customer_info: CustomerInfo
    

class OrderStatusUpdate(BaseModel):
    status: Literal['pending', 'confirmed', 'payment_received', 'processing', 'shipped', 'delivered', 'cancelled']
    updated_by: str
    notes: Optional[str] = None


class PaymentRecord(BaseModel):
    amount: Decimal
    method: str
    recorded_by: str = 'admin'
    notes: Optional[str] = None


class OrderItemResponse(BaseModel):
    id: str
    product_id: str
    product_name: str
    quantity: int
    price: Decimal


class StatusHistoryResponse(BaseModel):
    status: str
    updated_by: str
    notes: Optional[str] = None
    created_at: datetime


class OrderResponse(BaseModel):
    id: str
    order_id: str
    user_id: Optional[str]
    customer_name: str
    customer_email: EmailStr
    customer_phone: str
    delivery_address: Optional[str]
    pickup_preference: bool
    order_notes: Optional[str] = None
    payment_preference: str
    total: Decimal
    status: str
    payment_confirmed: bool
    payment_amount: Decimal
    payment_method: Optional[str]
    created_at: datetime
    updated_at: datetime
    items: Optional[List[OrderItemResponse]] = None
    status_history: Optional[List[StatusHistoryResponse]] = None


class OrderCreateResponse(BaseModel):
    success: bool
    message: str
    order_id: str
    total: Decimal
    status: str


class OrderListResponse(BaseModel):
    orders: List[OrderResponse]
    count: int
    page: Optional[int] = None
    total_pages: Optional[int] = None