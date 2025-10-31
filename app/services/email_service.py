import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from typing import Optional
import logging
import asyncio

# SendGrid imports
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailService:
    
    @staticmethod
    async def send_email_via_smtp(to_email: str, subject: str, html_content: str):
        """Send email via SMTP (Gmail) with anti-spam headers"""
        try:
            logger.info(f"Sending email via SMTP to {to_email}")
            
            # Validate SMTP configuration
            if not all([settings.SMTP_HOST, settings.SMTP_PORT, settings.SMTP_USER, settings.SMTP_PASSWORD]):
                logger.error("SMTP configuration is incomplete. Check environment variables.")
                return False
            
            message = MIMEMultipart('alternative')
            
            # Enhanced headers to reduce spam probability
            message['Subject'] = subject
            message['From'] = f"Crown Mega Store <{settings.SMTP_USER}>"
            message['To'] = to_email
            message['Reply-To'] = settings.BUSINESS_EMAIL
            message['X-Mailer'] = 'Crown Mega Store Order System'
            message['X-Priority'] = '3'
            message['X-MSMail-Priority'] = 'Normal'
            message['Importance'] = 'Normal'
            message['Content-Type'] = 'multipart/alternative'
            
            # Add plain text version for better deliverability
            from html import escape
            import re
            plain_text = re.sub('<[^<]+?>', '', html_content)
            plain_text = re.sub(r'\s+', ' ', plain_text).strip()
            
            text_part = MIMEText(plain_text, 'plain', 'utf-8')
            html_part = MIMEText(html_content, 'html', 'utf-8')
            
            message.attach(text_part)
            message.attach(html_part)
            
            logger.info(f"Connecting to SMTP server: {settings.SMTP_HOST}:{settings.SMTP_PORT}")
            
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                start_tls=True,
                timeout=30
            )
            
            logger.info(f"SMTP email successfully sent to {to_email}")
            return True
            
        except aiosmtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication failed: {str(e)}")
            return False
        except aiosmtplib.SMTPConnectError as e:
            logger.error(f"SMTP Connection failed: {str(e)}")
            return False
        except aiosmtplib.SMTPRecipientsRefused as e:
            logger.error(f"SMTP Recipients refused: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"SMTP email failed: {str(e)}")
            return False

    @staticmethod
    async def send_email_via_sendgrid(to_email: str, subject: str, html_content: str):
        """Send email via SendGrid API with improved deliverability"""
        try:
            if not SENDGRID_AVAILABLE:
                logger.error("SendGrid package not installed")
                return False
                
            if not settings.SENDGRID_API_KEY:
                logger.error("SendGrid API key not configured")
                return False
            
            logger.info(f"Sending email via SendGrid to {to_email}")
            
            # Create plain text version
            import re
            plain_text = re.sub('<[^<]+?>', '', html_content)
            plain_text = re.sub(r'\s+', ' ', plain_text).strip()
            
            # Create SendGrid message with enhanced deliverability settings
            message = Mail(
                from_email=(settings.FROM_EMAIL, "Crown Mega Store"),
                to_emails=to_email,
                subject=subject,
                html_content=html_content,
                plain_text_content=plain_text
            )
            
            # Add reply-to for better sender reputation
            message.reply_to = settings.BUSINESS_EMAIL
            
            # Add tracking settings (helps with deliverability)
            message.tracking_settings = {
                "click_tracking": {"enable": True, "enable_text": False},
                "open_tracking": {"enable": True},
                "subscription_tracking": {"enable": False},
                "ganalytics": {"enable": False}
            }
            
            # Add mail settings
            message.mail_settings = {
                "footer": {"enable": False},
                "sandbox_mode": {"enable": False}
            }
            
            # Send email
            sg = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
            
            # Run in executor to make it async
            def send_sync():
                return sg.send(message)
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, send_sync)
            
            if response.status_code >= 200 and response.status_code < 300:
                logger.info(f"SendGrid email successfully sent to {to_email}")
                return True
            else:
                logger.error(f"SendGrid API error: {response.status_code} - {response.body}")
                return False
                
        except Exception as e:
            logger.error(f"SendGrid email failed: {str(e)}")
            return False

    @staticmethod
    async def send_email(to_email: str, subject: str, html_content: str):
        """Send email using configured provider with fallback"""
        logger.info(f"Attempting to send email to {to_email} with provider: {settings.EMAIL_PROVIDER}")
        
        # Try primary provider
        if settings.EMAIL_PROVIDER.lower() == "sendgrid":
            success = await EmailService.send_email_via_sendgrid(to_email, subject, html_content)
            if success:
                return True
            logger.warning("SendGrid failed, trying SMTP fallback...")
            return await EmailService.send_email_via_smtp(to_email, subject, html_content)
        else:
            # Default to SMTP with SendGrid fallback
            success = await EmailService.send_email_via_smtp(to_email, subject, html_content)
            if success:
                return True
            
            # Fallback to SendGrid if available
            if SENDGRID_AVAILABLE and settings.SENDGRID_API_KEY:
                logger.warning("SMTP failed, trying SendGrid fallback...")
                return await EmailService.send_email_via_sendgrid(to_email, subject, html_content)
            
            logger.error("Both SMTP and SendGrid failed or unavailable")
            return False
        
    @staticmethod
    def format_order_email_business(order_data: dict) -> str:
        """Format HTML email for business owner"""
        items_html = ''
        for item in order_data['items']:
            subtotal = float(item['price']) * item['quantity']
            items_html += f"""
                <tr>
                    <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; font-size: 14px;">{item['product_name']}</td>
                    <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; text-align: center; font-size: 14px;">{item['quantity']}</td>
                    <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; text-align: right; font-size: 14px;">NGN {float(item['price']):.2f}</td>
                    <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; text-align: right; font-weight: 600; font-size: 14px;">NGN {subtotal:.2f}</td>
                </tr>"""
        
        delivery_info = order_data['customer_info'].get('delivery_address', 'Not specified')
        if order_data['customer_info'].get('pickup_preference'):
            delivery_info = "Customer prefers pickup"
            
        notes = order_data['customer_info'].get('order_notes', 'No special notes')
        
        return f"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>New Order Notification - Crown Mega Store</title>
    <style type="text/css">
        body {{ margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 14px; line-height: 1.6; color: #333333; background-color: #f4f4f4; }}
        table {{ border-collapse: collapse; }}
        .email-container {{ max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #2c5aa0 0%, #1e3d72 100%); color: #ffffff; padding: 30px 25px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 24px; font-weight: 600; }}
        .header p {{ margin: 8px 0 0 0; font-size: 16px; opacity: 0.9; }}
        .content {{ padding: 25px; }}
        .alert-box {{ background: #fff8dc; border: 1px solid #ffd700; border-radius: 6px; padding: 18px; margin-bottom: 20px; }}
        .order-section {{ background: #fafafa; border: 1px solid #e0e0e0; border-radius: 6px; padding: 20px; margin: 20px 0; }}
        .order-table {{ width: 100%; margin: 15px 0; }}
        .order-table th {{ background: #f8f9fa; padding: 12px; text-align: left; font-weight: 600; font-size: 13px; color: #555; border-bottom: 2px solid #dee2e6; }}
        .total-row {{ background: #e8f5e8; font-weight: 600; }}
        .customer-section {{ background: #f0f8ff; border: 1px solid #b3d9ff; border-radius: 6px; padding: 18px; margin: 20px 0; }}
        .action-section {{ background: #e6f3ff; border-left: 4px solid #0066cc; padding: 18px; margin: 20px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #888; font-size: 12px; background: #f8f9fa; }}
        .text-highlight {{ color: #2c5aa0; font-weight: 600; }}
        .amount {{ color: #28a745; font-weight: 600; font-size: 16px; }}
        .urgent {{ color: #dc3545; font-weight: 600; }}
        .info-row {{ margin: 8px 0; }}
        .info-label {{ font-weight: 600; color: #555; display: inline-block; width: 120px; }}
    </title>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>New Customer Order</h1>
            <p>Crown Mega Store Order Management</p>
        </div>
        
        <div class="content">
            <div class="alert-box">
                <strong class="urgent">Action Required:</strong> A new customer order has been placed and requires your attention within 2 hours.
            </div>
            
            <div class="order-section">
                <h2 style="margin-top: 0; color: #2c5aa0; font-size: 20px; border-bottom: 2px solid #e0e0e0; padding-bottom: 8px;">
                    Order Details #{order_data['order_id']}
                </h2>
                
                <table class="order-table" cellpadding="0" cellspacing="0">
                    <thead>
                        <tr>
                            <th>Product Name</th>
                            <th style="text-align: center; width: 80px;">Qty</th>
                            <th style="text-align: right; width: 100px;">Unit Price</th>
                            <th style="text-align: right; width: 100px;">Subtotal</th>
                        </tr>
                    </thead>
                    <tbody>{items_html}
                    </tbody>
                    <tfoot>
                        <tr class="total-row">
                            <td colspan="3" style="padding: 15px; text-align: right; font-weight: 600;">Order Total:</td>
                            <td style="padding: 15px; text-align: right;" class="amount">NGN {float(order_data['total']):.2f}</td>
                        </tr>
                    </tfoot>
                </table>
            </div>
            
            <div class="customer-section">
                <h3 style="margin-top: 0; color: #2c5aa0;">Customer Information</h3>
                <div class="info-row">
                    <span class="info-label">Full Name:</span>
                    <span>{order_data['customer_info']['name']}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Email Address:</span>
                    <span>{order_data['customer_info']['email']}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Phone Number:</span>
                    <span class="text-highlight">{order_data['customer_info']['phone']}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Delivery Info:</span>
                    <span>{delivery_info}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Payment Method:</span>
                    <span>{order_data['customer_info']['payment_preference']}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Special Notes:</span>
                    <span>{notes}</span>
                </div>
            </div>
            
            <div class="action-section">
                <h3 style="margin-top: 0; color: #0066cc;">Recommended Actions</h3>
                <ol style="margin: 10px 0; padding-left: 20px;">
                    <li style="margin: 6px 0;"><strong>Contact customer immediately</strong> - Call {order_data['customer_info']['phone']}</li>
                    <li style="margin: 6px 0;"><strong>Verify order accuracy</strong> - Confirm all items and delivery details</li>
                    <li style="margin: 6px 0;"><strong>Process payment</strong> - Share bank account details if needed</li>
                    <li style="margin: 6px 0;"><strong>Update order status</strong> - Mark as confirmed in your system</li>
                </ol>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Crown Mega Store</strong></p>
            <p>Order Management System | Placed: {order_data['created_at']}</p>
            <p>This is an automated notification from your e-commerce system.</p>
        </div>
    </div>
</body>
</html>"""
    
    @staticmethod
    def format_order_email_customer(order_data: dict) -> str:
        """Format HTML email for customer"""
        items_html = ""
        for item in order_data['items']:
            subtotal = float(item['price']) * item['quantity']
            items_html += f"""
                <tr>
                    <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; font-size: 14px;">{item['product_name']}</td>
                    <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; text-align: center; font-size: 14px;">{item['quantity']}</td>
                    <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; text-align: right; font-size: 14px;">NGN {float(item['price']):.2f}</td>
                    <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; text-align: right; font-weight: 600; font-size: 14px;">NGN {subtotal:.2f}</td>
                </tr>"""
        
        return f"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Order Confirmation - Crown Mega Store</title>
    <style type="text/css">
        body {{ margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 14px; line-height: 1.6; color: #333333; background-color: #f4f4f4; }}
        table {{ border-collapse: collapse; }}
        .email-container {{ max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #27ae60 0%, #1e8449 100%); color: #ffffff; padding: 30px 25px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 24px; font-weight: 600; }}
        .header p {{ margin: 8px 0 0 0; font-size: 16px; opacity: 0.9; }}
        .content {{ padding: 25px; }}
        .greeting {{ font-size: 16px; margin-bottom: 20px; }}
        .greeting strong {{ color: #27ae60; }}
        .intro-text {{ margin-bottom: 20px; line-height: 1.6; }}
        .next-steps {{ background: #fff8dc; border: 1px solid #ffd700; border-radius: 6px; padding: 18px; margin: 20px 0; }}
        .next-steps strong {{ color: #e67e22; }}
        .order-section {{ background: #fafafa; border: 1px solid #e0e0e0; border-radius: 6px; padding: 20px; margin: 20px 0; }}
        .order-table {{ width: 100%; margin: 15px 0; }}
        .order-table th {{ background: #f8f9fa; padding: 12px; text-align: left; font-weight: 600; font-size: 13px; color: #555; border-bottom: 2px solid #dee2e6; }}
        .total-row {{ background: #e8f5e8; font-weight: 600; }}
        .contact-section {{ background: #e8f4fd; border: 1px solid #b3d9ff; border-radius: 6px; padding: 18px; margin: 20px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #888; font-size: 12px; background: #f8f9fa; }}
        .amount {{ color: #27ae60; font-weight: 600; font-size: 18px; }}
        .contact-list {{ margin: 10px 0; padding: 0; list-style: none; }}
        .contact-list li {{ margin: 8px 0; padding: 5px 0; }}
        .contact-item {{ color: #2c5aa0; text-decoration: none; font-weight: 500; }}
        .order-number {{ color: #2c5aa0; font-weight: 600; }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>Order Confirmation</h1>
            <p>Crown Mega Store</p>
        </div>
        
        <div class="content">
            <div class="greeting">
                Hi <strong>{order_data['customer_info']['name']}</strong>,
            </div>
            
            <div class="intro-text">
                Thank you for choosing Crown Mega Store! We have successfully received your order and our team will contact you shortly to confirm all details and arrange payment and delivery.
            </div>
            
            <div class="next-steps">
                <strong>What happens next?</strong><br>
                Our customer service team will reach out to you within the next 2 hours via phone or email to confirm your order details and provide payment instructions.
            </div>
            
            <div class="order-section">
                <h2 style="margin-top: 0; color: #2c5aa0; font-size: 20px; border-bottom: 2px solid #e0e0e0; padding-bottom: 8px;">
                    Your Order <span class="order-number">#{order_data['order_id']}</span>
                </h2>
                
                <table class="order-table" cellpadding="0" cellspacing="0">
                    <thead>
                        <tr>
                            <th>Product Name</th>
                            <th style="text-align: center; width: 80px;">Qty</th>
                            <th style="text-align: right; width: 100px;">Unit Price</th>
                            <th style="text-align: right; width: 100px;">Subtotal</th>
                        </tr>
                    </thead>
                    <tbody>{items_html}
                    </tbody>
                    <tfoot>
                        <tr class="total-row">
                            <td colspan="3" style="padding: 15px; text-align: right; font-weight: 600;">Order Total:</td>
                            <td style="padding: 15px; text-align: right;" class="amount">NGN {float(order_data['total']):.2f}</td>
                        </tr>
                    </tfoot>
                </table>
            </div>
            
            <div class="contact-section">
                <h3 style="margin-top: 0; color: #2c5aa0;">Need to Make Changes?</h3>
                <p>If you need to modify or cancel this order, please contact us immediately using any of the following methods:</p>
                <ul class="contact-list">
                    <li>Email: <span class="contact-item">{settings.BUSINESS_EMAIL}</span></li>
                    <li>Phone: <span class="contact-item">{settings.BUSINESS_PHONE}</span></li>
                    <li>WhatsApp: <span class="contact-item">{settings.BUSINESS_WHATSAPP}</span></li>
                </ul>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Thank you for choosing Crown Mega Store!</strong></p>
            <p>Order Reference: #{order_data['order_id']} | Please keep this email for your records</p>
            <p>This is an automated confirmation from Crown Mega Store.</p>
        </div>
    </div>
</body>
</html>"""
    
    @staticmethod
    def format_status_update_email(order: dict, new_status: str, notes: Optional[str] = None) -> tuple[str, str]:
        """Format status update email - returns (subject, html_content)"""
        status_messages = {
            'confirmed': {
                'title': 'Order Confirmed',
                'message': "Great news! We have confirmed your order and will send payment details shortly.",
                'color': '#27ae60'
            },
            'payment_received': {
                'title': 'Payment Received',
                'message': "We have received your payment! Your order is now being processed.",
                'color': '#2c5aa0'
            },
            'processing': {
                'title': 'Order Processing',
                'message': "Your order is being prepared for delivery.",
                'color': '#f39c12'
            },
            'shipped': {
                'title': 'Order Shipped',
                'message': "Your order has been shipped and is on its way to you!",
                'color': '#e67e22'
            },
            'delivered': {
                'title': 'Order Delivered',
                'message': "Your order has been delivered successfully! Thank you for shopping with us.",
                'color': '#27ae60'
            },
            'cancelled': {
                'title': 'Order Cancelled',
                'message': "Your order has been cancelled as requested.",
                'color': '#e74c3c'
            }
        }
        
        status_info = status_messages.get(new_status, {
            'title': 'Order Status Update',
            'message': f"Your order status has been updated to: {new_status.replace('_', ' ').title()}",
            'color': '#2c5aa0'
        })
        
        subject = f"Order Update: {status_info['title']} - #{order['order_id']}"
        
        html_content = f"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{status_info['title']} - Crown Mega Store</title>
    <style type="text/css">
        body {{ margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 14px; line-height: 1.6; color: #333333; background-color: #f4f4f4; }}
        table {{ border-collapse: collapse; }}
        .email-container {{ max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, {status_info['color']} 0%, {status_info['color']}dd 100%); color: #ffffff; padding: 30px 25px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 24px; font-weight: 600; }}
        .content {{ padding: 25px; }}
        .message-box {{ background: #f8f9fa; border-left: 4px solid {status_info['color']}; padding: 18px; margin: 20px 0; border-radius: 0 6px 6px 0; }}
        .order-details {{ background: #fafafa; border: 1px solid #e0e0e0; border-radius: 6px; padding: 20px; margin: 20px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #888; font-size: 12px; background: #f8f9fa; }}
        .status-highlight {{ color: {status_info['color']}; font-weight: 600; }}
        .amount {{ color: #27ae60; font-weight: 600; }}
        .note-box {{ background: #fff8dc; border: 1px solid #ffd700; border-radius: 6px; padding: 15px; margin: 15px 0; }}
        .info-row {{ margin: 8px 0; }}
        .info-label {{ font-weight: 600; color: #555; display: inline-block; width: 80px; }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>{status_info['title']}</h1>
            <p>Crown Mega Store</p>
        </div>
        
        <div class="content">
            <p style="font-size: 16px;">Hi <strong>{order['customer_name']}</strong>,</p>
            
            <div class="message-box">
                <p style="margin: 0; font-size: 15px;">{status_info['message']}</p>
            </div>
            
            {f'<div class="note-box"><strong>Additional Information:</strong><br>{notes}</div>' if notes else ''}
            
            <div class="order-details">
                <h3 style="margin-top: 0; color: #2c5aa0;">Order Summary</h3>
                <div class="info-row">
                    <span class="info-label">Order ID:</span>
                    <span class="status-highlight">#{order['order_id']}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Total:</span>
                    <span class="amount">NGN {float(order['total']):.2f}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Status:</span>
                    <span class="status-highlight">{new_status.replace('_', ' ').title()}</span>
                </div>
            </div>
            
            <p>Thank you for choosing Crown Mega Store! We appreciate your business.</p>
            
            <div style="background: #e8f4fd; border: 1px solid #b3d9ff; border-radius: 6px; padding: 15px; margin: 20px 0;">
                <p style="margin: 5px 0; font-size: 13px; color: #555;">
                    <strong>Questions or concerns?</strong><br>
                    Contact us at {settings.BUSINESS_EMAIL} or call {settings.BUSINESS_PHONE}
                </p>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Crown Mega Store</strong></p>
            <p>This is an automated update from your order management system.</p>
        </div>
    </div>
</body>
</html>"""
        
        return subject, html_content