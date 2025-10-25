import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from typing import Optional


class EmailService:
    
    @staticmethod
    async def send_email(to_email: str, subject: str, html_content: str):
        """Send HTML email"""
        try:
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = settings.SMTP_USER
            message['To'] = to_email
            
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)
            
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                start_tls=True
            )
            
            return True
        except Exception as e:
            print(f"Email sending failed: {str(e)}")
            return False
        
    @staticmethod
    def format_order_email_business(order_data: dict) -> str:
        """Format HTML email for business owner"""
        items_html = ''
        for item in order_data['items']:
            subtotal = float(item['price']) * item['quantity']
            items_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">{item['product_name']}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center;">{item['quantity']}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">₦{float(item['price']):.2f}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right; font-weight: bold;">₦{subtotal:.2f}</td>
            </tr>
            """
        
        delivery_info = order_data['customer_info'].get('delivery_address', 'N/A')
        if order_data['customer_info'].get('pickup_preference'):
            delivery_info = "<strong style='color: #e74c3c;'>PICKUP PREFERRED</strong>"
            
        notes = order_data['customer_info'].get('order_notes', 'None')
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #2c5aa0; color: white; padding: 20px; border-radius: 5px 5px 0 0; }}
                .content {{ background: #f9f9f9; padding: 20px; }}
                .order-details {{ background: white; padding: 20px; border-radius: 5px; margin: 15px 0; }}
                .customer-info {{ background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .action-box {{ background: #d1ecf1; padding: 15px; border-left: 4px solid #17a2b8; margin: 15px 0; }}
                table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                .total-row {{ background: #f8f9fa; font-weight: bold; font-size: 18px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">🆕 New Order Received!</h1>
                    <p style="margin: 5px 0 0 0;">Crown Mega Store</p>
                </div>
                
                <div class="content">
                    <div style="background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin-bottom: 15px;">
                        <strong>⚡ Quick Action Required:</strong> New customer order needs confirmation
                    </div>
                    
                    <div class="order-details">
                        <h2 style="color: #2c5aa0; border-bottom: 2px solid #eee; padding-bottom: 10px;">
                            Order #{order_data['order_id']}
                        </h2>
                        
                        <table>
                            <thead>
                                <tr style="background: #f8f9fa;">
                                    <th style="padding: 10px; text-align: left;">Product</th>
                                    <th style="padding: 10px; text-align: center;">Qty</th>
                                    <th style="padding: 10px; text-align: right;">Price</th>
                                    <th style="padding: 10px; text-align: right;">Subtotal</th>
                                </tr>
                            </thead>
                            <tbody>
                                {items_html}
                            </tbody>
                            <tfoot>
                                <tr class="total-row">
                                    <td colspan="3" style="padding: 15px; text-align: right;">TOTAL:</td>
                                    <td style="padding: 15px; text-align: right; color: #e74c3c; font-size: 20px;">
                                        ₦{float(order_data['total']):.2f}
                                    </td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                    
                    <div class="customer-info">
                        <h3 style="margin-top: 0; color: #2c5aa0;">👤 Customer Information</h3>
                        <p><strong>Name:</strong> {order_data['customer_info']['name']}</p>
                        <p><strong>Email:</strong> {order_data['customer_info']['email']}</p>
                        <p><strong>Phone:</strong> {order_data['customer_info']['phone']}</p>
                        <p><strong>Delivery:</strong> {delivery_info}</p>
                        <p><strong>Payment Preference:</strong> {order_data['customer_info']['payment_preference']}</p>
                        <p><strong>Special Notes:</strong> {notes}</p>
                    </div>
                    
                    <div class="action-box">
                        <h3 style="margin-top: 0;">📞 Next Steps:</h3>
                        <ol>
                            <li><strong>Contact customer within 2 hours</strong> - Call {order_data['customer_info']['phone']}</li>
                            <li><strong>Confirm order details</strong> - Verify items and delivery address</li>
                            <li><strong>Share payment details</strong> - Send bank account information</li>
                            <li><strong>Update order status</strong> - Mark as "confirmed" in dashboard</li>
                        </ol>
                    </div>
                </div>
                
                <div style="text-align: center; padding: 15px; color: #666; font-size: 12px;">
                    <p>Crown Mega Store - Order Management System</p>
                    <p>Order placed: {order_data['created_at']}</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    @staticmethod
    def format_order_email_customer(order_data: dict) -> str:
        """Format HTML email for customer"""
        items_html = ""
        for item in order_data['items']:
            subtotal = float(item['price']) * item['quantity']
            items_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">{item['product_name']}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center;">{item['quantity']}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">₦{float(item['price']):.2f}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right; font-weight: bold;">₦{subtotal:.2f}</td>
            </tr>
            """
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #27ae60; color: white; padding: 20px; border-radius: 5px 5px 0 0; }}
                .content {{ background: #f9f9f9; padding: 20px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                .total-row {{ background: #f8f9fa; font-weight: bold; font-size: 18px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">✅ Order Confirmation</h1>
                    <p style="margin: 5px 0 0 0;">Crown Mega Store</p>
                </div>
                
                <div class="content">
                    <p>Hi <strong>{order_data['customer_info']['name']}</strong>,</p>
                    
                    <p>Thank you for your order! We've received your order and our team will contact you shortly to confirm the details and arrange payment and delivery.</p>
                    
                    <div style="background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 15px 0;">
                        <strong>🎯 What happens next?</strong><br>
                        Our team will call or email you within the next 2 hours to confirm your order and share payment details.
                    </div>
                    
                    <div style="background: white; padding: 20px; border-radius: 5px; margin: 15px 0;">
                        <h2 style="color: #2c5aa0; border-bottom: 2px solid #eee; padding-bottom: 10px;">
                            Order #{order_data['order_id']}
                        </h2>
                        
                        <table>
                            <thead>
                                <tr style="background: #f8f9fa;">
                                    <th style="padding: 10px; text-align: left;">Product</th>
                                    <th style="padding: 10px; text-align: center;">Qty</th>
                                    <th style="padding: 10px; text-align: right;">Price</th>
                                    <th style="padding: 10px; text-align: right;">Subtotal</th>
                                </tr>
                            </thead>
                            <tbody>
                                {items_html}
                            </tbody>
                            <tfoot>
                                <tr class="total-row">
                                    <td colspan="3" style="padding: 15px; text-align: right;">ORDER TOTAL:</td>
                                    <td style="padding: 15px; text-align: right; color: #27ae60; font-size: 20px;">
                                        ₦{float(order_data['total']):.2f}
                                    </td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                    
                    <div style="background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 15px 0;">
                        <h3 style="margin-top: 0;">📞 Need to Make Changes?</h3>
                        <p>If you need to modify or cancel this order, please contact us immediately:</p>
                        <ul>
                            <li>📧 Email: {settings.BUSINESS_EMAIL}</li>
                            <li>📱 Phone: {settings.BUSINESS_PHONE}</li>
                            <li>💬 WhatsApp: {settings.BUSINESS_WHATSAPP}</li>
                        </ul>
                    </div>
                </div>
                
                <div style="text-align: center; padding: 15px; color: #666; font-size: 12px;">
                    <p><strong>Thank you for choosing Crown Mega Store!</strong></p>
                    <p>Order Reference: #{order_data['order_id']} | Keep this email for your records</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    @staticmethod
    def format_status_update_email(order: dict, new_status: str, notes: Optional[str] = None) -> tuple[str, str]:
        """Format status update email - returns (subject, html_content)"""
        status_messages = {
            'confirmed': {
                'emoji': '✅',
                'title': 'Order Confirmed',
                'message': "Great news! We've confirmed your order and will send payment details shortly."
            },
            'payment_received': {
                'emoji': '💰',
                'title': 'Payment Received',
                'message': "We've received your payment! Your order is now being processed."
            },
            'processing': {
                'emoji': '📦',
                'title': 'Order Processing',
                'message': "Your order is being prepared for delivery."
            },
            'shipped': {
                'emoji': '🚚',
                'title': 'Order Shipped',
                'message': "Your order has been shipped and is on its way!"
            },
            'delivered': {
                'emoji': '🎉',
                'title': 'Order Delivered',
                'message': "Your order has been delivered successfully! Thank you for shopping with us."
            },
            'cancelled': {
                'emoji': '❌',
                'title': 'Order Cancelled',
                'message': "Your order has been cancelled as requested."
            }
        }
        
        status_info = status_messages.get(new_status, {
            'emoji': '📋',
            'title': 'Order Status Update',
            'message': f"Your order status has been updated to: {new_status.replace('_', ' ').title()}"
        })
        
        subject = f"{status_info['emoji']} {status_info['title']} - Order #{order['order_id']}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #2c5aa0; color: white; padding: 20px; border-radius: 5px; }}
                .content {{ background: #f9f9f9; padding: 20px; border-radius: 5px; margin: 15px 0; }}
                .order-box {{ background: white; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">{status_info['emoji']} {status_info['title']}</h1>
                </div>
                
                <div class="content">
                    <p>Hi <strong>{order['customer_name']}</strong>,</p>
                    <p>{status_info['message']}</p>
                    
                    {f'<div style="background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 15px 0;"><strong>Note:</strong> {notes}</div>' if notes else ''}
                    
                    <div class="order-box">
                        <p><strong>Order ID:</strong> {order['order_id']}</p>
                        <p><strong>Total:</strong> ₦{float(order['total']):.2f}</p>
                        <p><strong>Status:</strong> {new_status.replace('_', ' ').title()}</p>
                    </div>
                    
                    <p>Thank you for choosing Crown Mega Store!</p>
                    <p style="font-size: 12px; color: #666;">
                        Questions? Contact us at {settings.BUSINESS_EMAIL} or {settings.BUSINESS_PHONE}
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return subject, html_content