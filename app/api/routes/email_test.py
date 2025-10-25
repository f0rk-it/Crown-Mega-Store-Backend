from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.services.email_service import EmailService
from app.core.config import settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class EmailTestRequest(BaseModel):
    to_email: EmailStr
    test_message: str = "This is a test email from Crown Mega Store API"


@router.post("/test-email")
async def test_email_service(request: EmailTestRequest):
    """Test email service - for debugging purposes only"""
    
    # Basic security check - only allow in development or to business email
    if settings.ENVIRONMENT == "production" and request.to_email != settings.BUSINESS_EMAIL:
        raise HTTPException(status_code=403, detail="Email testing is restricted in production")
    
    try:
        logger.info(f"Testing email service to: {request.to_email}")
        
        # Simple test email content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; }}
                .container {{ max-width: 500px; margin: 0 auto; }}
                .header {{ background: #2c5aa0; color: white; padding: 15px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>✅ Email Test Successful</h2>
                </div>
                <div style="padding: 20px; background: #f9f9f9; margin-top: 10px; border-radius: 5px;">
                    <p><strong>Message:</strong> {request.test_message}</p>
                    <p><strong>From:</strong> Crown Mega Store API</p>
                    <p><strong>Environment:</strong> {settings.ENVIRONMENT}</p>
                    <p><strong>SMTP Host:</strong> {settings.SMTP_HOST}</p>
                    <p><strong>SMTP Port:</strong> {settings.SMTP_PORT}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        success = await EmailService.send_email(
            to_email=request.to_email,
            subject="🧪 Email Service Test - Crown Mega Store",
            html_content=html_content
        )
        
        if success:
            return {
                "success": True,
                "message": f"Test email sent successfully to {request.to_email}",
                "smtp_config": {
                    "host": settings.SMTP_HOST,
                    "port": settings.SMTP_PORT,
                    "user": settings.SMTP_USER,
                    "environment": settings.ENVIRONMENT
                }
            }
        else:
            return {
                "success": False,
                "message": "Email sending failed. Check logs for details.",
                "smtp_config": {
                    "host": settings.SMTP_HOST,
                    "port": settings.SMTP_PORT,
                    "user": settings.SMTP_USER,
                    "environment": settings.ENVIRONMENT
                }
            }
            
    except Exception as e:
        logger.error(f"Email test failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Email test failed: {str(e)}"
        )


@router.get("/email-config")
async def get_email_config():
    """Get current email configuration (for debugging)"""
    
    return {
        "smtp_host": settings.SMTP_HOST,
        "smtp_port": settings.SMTP_PORT,
        "smtp_user": settings.SMTP_USER,
        "business_email": settings.BUSINESS_EMAIL,
        "environment": settings.ENVIRONMENT,
        "password_set": bool(settings.SMTP_PASSWORD),
        "password_length": len(settings.SMTP_PASSWORD) if settings.SMTP_PASSWORD else 0
    }