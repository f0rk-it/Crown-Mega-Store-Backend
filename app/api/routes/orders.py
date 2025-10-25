from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from app.schemas.order import (OrderCreate, OrderResponse, OrderStatusUpdate, PaymentRecord, OrderCreateResponse, OrderListResponse)
from app.services.order_service import OrderService
from app.api.deps import get_current_active_user, get_current_admin_user

router = APIRouter()

@router.post('/checkout', response_model=OrderCreateResponse)
async def create_order(order: OrderCreate, current_user: Optional[dict] = Depends(get_current_active_user)):
    """
    Create new order and send email notifications.
    Can be used by authenticated or guest users
    Returns JSON response only (emails are sent in background)
    """
    try:
        user_id = current_user.get('sub') if current_user else None
        
        order_data = {
            'items': [item.model_dump() for item in order.items],
            'customer_info': order.customer_info.model_dump()
        }
        
        created_order = await OrderService.create_order(order_data, user_id)
        
        return OrderCreateResponse(
            success=True,
            message='Order created successfully! Check your email for confirmation.',
            order_id=created_order['order_id'],
            total=float(created_order['total']),
            status=created_order['status']
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Order creation failed: {str(e)}"
        )

@router.get('/{order_id}', response_model=OrderResponse)
async def get_order(order_id: str):
    """Get order details by Order ID - returns JSON only"""
    order = OrderService.get_order_by_id(order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Order not found'
        )
        
    return order

@router.get('/user/my-orders', response_model=OrderListResponse)
async def get_my_orders(current_user: dict = Depends(get_current_active_user), status: Optional[str] = None):
    """Get all orders for current authenticated user"""
    try:
        user_id = current_user['sub']
        print(f"Getting orders for user: {user_id}")
        
        orders = OrderService.get_user_orders(user_id, status)
        
        print(f"Found {len(orders)} orders")
        
        return OrderListResponse(orders=orders, count=len(orders))
        
    except Exception as e:
        print(f"Error in get_my_orders: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch orders: {str(e)}"
        )

@router.post('/{order_id}/status', response_model=OrderResponse, dependencies=[Depends(get_current_admin_user)])
async def update_order_status(order_id: str, status_update: OrderStatusUpdate):
    """
    Update order status (Admin only)
    Email notification is sent to customer automatically
    """
    updated_order = await OrderService.update_order_status(
        order_id,
        status_update.model_dump()
    )
    
    if not updated_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Order not found'
        )
    
    return updated_order

@router.post('/{order_id}/payment', response_model=OrderResponse, dependencies=[Depends(get_current_admin_user)])
async def record_payment(order_id: str, payment_data: PaymentRecord):
    """
    Record payment for order (Admin only)
    Email notification is sent to customer automatically.
    """
    updated_order = await OrderService.record_payment(order_id, payment_data.model_dump())
    
    if not updated_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Order not found'
        )
    
    return updated_order

@router.get('/', response_model=OrderListResponse, dependencies=[Depends(get_current_admin_user)])
async def get_all_orders(status: Optional[str] = None, limit: int = Query(50, ge=1, le=100), page: int = Query(1, ge=1)):
    """Get all orders with pagination"""
    result = OrderService.get_all_orders(status, limit, page)
    
    return OrderListResponse(
        orders=result['orders'],
        count=result['count'],
        page=result['page'],
        total_pages=result['total_pages']
    )
    
@router.get('/stats/dashboard', dependencies=[Depends(get_current_admin_user)])
async def get_order_stats():
    """Get order statistics for admin dashboard"""
    from app.core.database import get_db
    from collections import Counter
    
    db = get_db()
    
    # Get all orders
    all_orders = db.table('orders').select('*').execute().data
    
    # Calculate statistics
    total_orders = len(all_orders)
    total_revenue = sum(float(order['total']) for order in all_orders if order.get('payment_confirmed') or order['status'] == 'delivered')
    pending_orders = len([o for o in all_orders if o['status'] == 'pending'])
    confirmed_orders = len([o for o in all_orders if o['status'] == 'confirmed'])
    completed_orders = len([o for o in all_orders if o['status'] == 'delivered'])
    
    # Status breakdown
    status_counts = Counter(order['status'] for order in all_orders)
    
    # Recent orders (last 7 days)
    from datetime import datetime, timedelta
    seven_days_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
    recent_orders = [o for o in all_orders if o['created_at'] >= seven_days_ago]
    
    # Average order value
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    return {
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2),
        "pending_orders": pending_orders,
        "confirmed_orders": confirmed_orders,
        "completed_orders": completed_orders,
        "recent_orders_count": len(recent_orders),
        "average_order_value": round(avg_order_value, 2),
        "status_breakdown": dict(status_counts),
        "payment_confirmed_count": len([o for o in all_orders if o.get('payment_confirmed') or o['status'] == 'delivered'])
    }