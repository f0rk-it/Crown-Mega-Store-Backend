from typing import List, Optional
from app.core.database import get_db
from app.utils.order_id_generator import generate_order_id
from app.services.email_service import EmailService
from datetime import datetime
from app.core.config import settings


class OrderService:
    
    @staticmethod
    async def create_order(order_data: dict, user_id: Optional[str] = None):
        """Create new order and send email notifications"""
        db = get_db()
        
        # Generate unique order ID
        order_id = generate_order_id()
        
        # Calculate total
        total = sum(float(item['price']) * item['quantity'] for item in order_data['items'])
        
        # Prepare order data for database
        order_record = {
            'order_id':order_id,
            'user_id': user_id,
            'customer_name': order_data['customer_info']['name'],
            'customer_email': order_data['customer_info']['email'],
            'customer_phone': order_data['customer_info']['phone'],
            'delivery_address': order_data['customer_info'].get('delivery_address'),
            'pickup_preference': order_data['customer_info'].get('pickup_preference', False),
            'order_notes': order_data['customer_info'].get('order_notes'),
            'payment_preference': order_data['customer_info'].get('payment_preference', 'bank_transfer'),
            'total': total,
            'status': 'pending',
            'payment_confirmed': False,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Insert order into database
        order_result = db.table('orders').insert(order_record).execute()
        created_order = order_result.data[0]
        
        # Insert order items
        for item in order_data['items']:
            item_record = {
                'order_id': created_order['id'],
                'product_id': item['product_id'],
                'product_name': item['product_name'],
                'quantity': item['quantity'],
                'price': float(item['price']),
                'created_at': datetime.utcnow().isoformat(),
            }
            db.table('order_items').insert(item_record).execute()
        
        # Create initial status history entry
        status_history = {
            'order_id': created_order['id'],
            'status': 'pending',
            'updated_by': 'system',
            'notes': 'Order created from website checkout',
            'created_at': datetime.utcnow().isoformat()
        }
        db.table('order_status_history').insert(status_history).execute()
        
        # Update product order counts
        for item in order_data['items']:
            product = db.table('products').select('order_count').eq('id', item['product_id']).execute()
            if product.data:
                new_count = product.data[0].get('order_count', 0) + item['quantity']
                db.table('products').update({
                    'order_count': new_count,
                    'updated_at': datetime.utcnow().isoformat()
                }).eq('id', item['product_id']).execute()
            
        # Prepare email data
        email_data = {
            'order_id': order_id,
            'items': order_data['items'],
            'customer_info': order_data['customer_info'],
            'total': total,
            'created_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Send emails
        business_html = EmailService.format_order_email_business(email_data)
        customer_html = EmailService.format_order_email_customer(email_data)
        
        await EmailService.send_email(
            settings.BUSINESS_EMAIL,
            f"New Order #{order_id} - ₦{total:.2f}",
            business_html
        )
        
        await EmailService.send_email(
            order_data['customer_info']['email'],
            f"Order Confirmation #{order_id} - Crown Mega Store",
            customer_html
        )
        
        return created_order

    @staticmethod
    def get_order_by_id(order_id: str, include_items: bool = True):
        """Get order details with items"""
        db = get_db()
        
        # Get order
        result = db.table('orders').select('*').eq('order_id', order_id).execute()
        
        if not result.data:
            return None

        order = result.data[0]
        
        if include_items:
            # Get order items
            items_result = db.table('order_items').select('*').eq('order_id', order['id']).execute()
            order['items'] = items_result.data
            
            # Get status history
            history_result = db.table('order_status_history').select('*').eq('order_id', order['id']).order('created_at').execute()
            order['status_history'] = history_result.data
        
        return order
    
    @staticmethod
    async def update_order_status(order_id: str, status_update: dict):
        """Update order status and send notifications"""
        db = get_db()
        
        # Get order
        order = OrderService.get_order_by_id(order_id, include_items=False)
        if not order:
            return None
        
        old_status = order['status']
        new_status = status_update['status']
        
        # Update order status
        db.table('orders').update({
            'status': new_status,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('order_id', order_id).execute()
        
        # Add to status history
        history_entry = {
            'order_id': order['id'],
            'status': new_status,
            'updated_by': status_update['updated_by'],
            'notes': status_update.get('notes'),
            'created_at': datetime.utcnow().isoformat()
        }
        db.table('order_status_history').insert(history_entry).execute()
        
        # Send customer notification email
        subject, html_content = EmailService.format_status_update_email(order, new_status, status_update.get('notes'))
        await EmailService.send_email(order['customer_email'], subject, html_content)
        
        # Get updated order
        updated_order = OrderService.get_order_by_id(order_id)
        
        return updated_order
    
    @staticmethod
    async def record_payment(order_id: str, payment_data: dict):
        """Record payment for order"""
        db = get_db()
        
        order = OrderService.get_order_by_id(order_id, include_items=False)
        if not order:
            return None
        
        # Update order with payment info
        db.table('orders').update({
            'payment_confirmed': True,
            'payment_amount': float(payment_data.get('amount')),
            'payment_method': payment_data.get('method'),
            'status': 'payment_received',
            'updated_at': datetime.utcnow().isoformat()
        }).eq('order_id', order_id).execute()
        
        # Add to status history
        notes = payment_data.get('notes') or f"Payment of ₦{float(payment_data.get('amount')):.2f} via {payment_data.get('method')}"
        history_entry = {
            'order_id': order['id'],
            'status': 'payment_received',
            'updated_by': payment_data.get('recorded_by', 'admin'),
            'notes': notes,
            'created_at': datetime.utcnow().isoformat()
        }
        db.table('order_status_history').insert(history_entry).execute()
        
        # Send email notification
        subject, html_content = EmailService.format_status_update_email(order, 'payment_received', notes)
        await EmailService.send_email(order['customer_email'], subject, html_content)
        
        # Get updated order
        updated_order = OrderService.get_order_by_id(order_id)
        
        return updated_order
    
    @staticmethod
    def get_user_orders(user_id: str, status: Optional[str] = None):
        """Get all orders for a user"""
        try:
            db = get_db()
            
            query = db.table('orders').select('*').eq('user_id', user_id)
            
            if status:
                query = query.eq('status', status)
                
            result = query.order('created_at', desc=True).execute()
            
            print(f"Database query for user_id: {user_id}")
            print(f"Query result: {result}")
            
            return result.data if result.data else []
        
        except Exception as e:
            print(f"Error in get_user_orders: {str(e)}")
            print(f"User ID: {user_id}")
            raise e
    
    @staticmethod
    def get_all_orders(status: Optional[str] = None, limit: int = 50, page: int = 1):
        """Get all orders with pagination (admin)"""
        db = get_db()
        
        offset = (page - 1) * limit
        
        query = db.table('orders').select('*')
        
        if status:
            query = query.eq('status', status)

        result = query.order('created_at', desc=True).limit(limit).range(offset, offset + limit - 1).execute()
        
        # Get total count for pagination
        count_query = db.table('orders').select('id', count='exact')
        if status:
            count_query = count_query.eq('status', status)
        count_result = count_query.execute()
        
        total_count = count_result.count if hasattr(count_result, 'count') else len(result.data)
        total_pages = (total_count + limit - 1) // limit
        
        return {
            'orders': result.data,
            'count': len(result.data),
            'page': page,
            'total_pages': total_pages,
            'total_count': total_count
        }