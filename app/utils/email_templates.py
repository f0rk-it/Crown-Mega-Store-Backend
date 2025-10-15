from typing import Dict, Any

def get_welcome_email(user_name: str) -> str:
    """Welcome email template for new users"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #2c5aa0; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background: #f9f9f9; }}
            .button {{ background: #27ae60; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 15px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to Crown Mega Store! 🎉</h1>
            </div>
            
            <div class="content">
                <p>Hi <strong>{user_name}</strong>,</p>
                
                <p>Thank you for joining Crown Mega Store! We're excited to have you as part of our community.</p>
                
                <p>Here's what you can do now:</p>
                <ul>
                    <li>Browse our wide selection of products</li>
                    <li>Get personalized product recommendations</li>
                    <li>Track your orders in real-time</li>
                    <li>Enjoy exclusive deals and offers</li>
                </ul>
                
                <a href="https://crownmegastore.com/shop" class="button">Start Shopping</a>
                
                <p>If you have any questions, feel free to reach out to us!</p>
                
                <p>Happy shopping!<br>
                The Crown Mega Store Team</p>
            </div>
        </div>
    </body>
    </html>
    """

def get_password_reset_email(user_name: str, reset_link: str) -> str:
    """Password reset email template"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #2c5aa0; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background: #f9f9f9; }}
            .button {{ background: #e74c3c; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 15px 0; }}
            .warning {{ background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 15px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Password Reset Request</h1>
            </div>
            
            <div class="content">
                <p>Hi <strong>{user_name}</strong>,</p>
                
                <p>We received a request to reset your password. Click the button below to create a new password:</p>
                
                <a href="{reset_link}" class="button">Reset Password</a>
                
                <div class="warning">
                    <strong>⚠️ Security Notice:</strong><br>
                    This link will expire in 1 hour. If you didn't request this reset, please ignore this email.
                </div>
                
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all;">{reset_link}</p>
                
                <p>Best regards,<br>
                Crown Mega Store Security Team</p>
            </div>
        </div>
    </body>
    </html>
    """

def get_order_shipped_email(order_data: Dict[str, Any]) -> str:
    """Order shipped notification email template"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #27ae60; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background: #f9f9f9; }}
            .tracking-box {{ background: white; padding: 20px; border-radius: 5px; margin: 15px 0; text-align: center; }}
            .tracking-number {{ font-size: 24px; font-weight: bold; color: #2c5aa0; letter-spacing: 2px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚚 Your Order is On The Way!</h1>
            </div>
            
            <div class="content">
                <p>Hi <strong>{order_data.get('customer_name')}</strong>,</p>
                
                <p>Great news! Your order <strong>#{order_data.get('order_id')}</strong> has been shipped and is on its way to you!</p>
                
                <div class="tracking-box">
                    <p style="margin: 0; color: #666;">Tracking Number:</p>
                    <p class="tracking-number">{order_data.get('tracking_number', 'N/A')}</p>
                </div>
                
                <p><strong>Estimated Delivery:</strong> {order_data.get('estimated_delivery', '2-3 business days')}</p>
                
                <p><strong>Order Summary:</strong></p>
                <ul>
                    <li>Order Total: ${order_data.get('total', 0):.2f}</li>
                    <li>Delivery Address: {order_data.get('delivery_address', 'N/A')}</li>
                </ul>
                
                <p>Thank you for shopping with Crown Mega Store!</p>
                
                <p>Best regards,<br>
                Crown Mega Store Team</p>
            </div>
        </div>
    </body>
    </html>
    """

def get_low_stock_alert_email(product_data: Dict[str, Any]) -> str:
    """Low stock alert email for admin"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #e74c3c; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background: #f9f9f9; }}
            .alert {{ background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 15px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>⚠️ Low Stock Alert</h1>
            </div>
            
            <div class="content">
                <p>Hi Admin,</p>
                
                <div class="alert">
                    <strong>Action Required:</strong> The following product is running low on stock.
                </div>
                
                <p><strong>Product Details:</strong></p>
                <ul>
                    <li>Name: {product_data.get('name')}</li>
                    <li>Category: {product_data.get('category')}</li>
                    <li>Current Stock: <strong style="color: #e74c3c;">{product_data.get('stock_quantity')} units</strong></li>
                    <li>Price: ${product_data.get('price', 0):.2f}</li>
                </ul>
                
                <p>Consider restocking this item to avoid running out.</p>
                
                <p>Crown Mega Store Inventory System</p>
            </div>
        </div>
    </body>
    </html>
    """

def get_promotional_email(promo_data: Dict[str, Any]) -> str:
    """Promotional email template"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
            .content {{ padding: 20px; background: #f9f9f9; }}
            .promo-box {{ background: #fff3cd; padding: 20px; border-radius: 10px; text-align: center; margin: 20px 0; }}
            .promo-code {{ font-size: 28px; font-weight: bold; color: #e74c3c; letter-spacing: 3px; }}
            .button {{ background: #27ae60; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 15px 0; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 {promo_data.get('title', 'Special Offer Just For You!')}</h1>
            </div>
            
            <div class="content">
                <p>Hi there! 👋</p>
                
                <p>{promo_data.get('message', 'We have an exclusive offer just for you!')}</p>
                
                <div class="promo-box">
                    <p style="margin: 0; color: #666; font-size: 14px;">Use Promo Code:</p>
                    <p class="promo-code">{promo_data.get('promo_code', 'SAVE20')}</p>
                    <p style="margin: 0; color: #666;">Get {promo_data.get('discount', '20')}% OFF</p>
                </div>
                
                <p><strong>Offer Valid Until:</strong> {promo_data.get('expiry_date', 'Limited Time')}</p>
                
                <div style="text-align: center;">
                    <a href="{promo_data.get('shop_link', 'https://crownmegastore.com')}" class="button">Shop Now</a>
                </div>
                
                <p style="font-size: 12px; color: #666;">
                    Terms and conditions apply. This offer cannot be combined with other promotions.
                </p>
                
                <p>Happy Shopping!<br>
                Crown Mega Store Team</p>
            </div>
        </div>
    </body>
    </html>
    """