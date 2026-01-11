"""Test script for Resend email functionality"""
import asyncio
from app.services.email_service import EmailService
from app.core.config import settings

async def test_resend_email():
    """Test sending email via Resend"""
    
    print("=" * 60)
    print("Testing Resend Email Service")
    print("=" * 60)
    print(f"Email Provider: {settings.EMAIL_PROVIDER}")
    print(f"Resend API Key configured: {'Yes' if settings.RESEND_API_KEY else 'No'}")
    print("-" * 60)
    
    # Test email details
    to_email = input("Enter your email address to receive test email: ").strip()
    
    if not to_email:
        print("❌ No email address provided!")
        return
    
    subject = "Test Email from Crown Mega Store"
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: #2c5aa0; color: white; padding: 20px; text-align: center; border-radius: 5px; }
            .content { padding: 20px; background: #f9f9f9; border-radius: 5px; margin-top: 20px; }
            .success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 15px; border-radius: 5px; margin: 15px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✅ Test Email Successful!</h1>
            </div>
            
            <div class="content">
                <div class="success">
                    <strong>Success!</strong> Your Resend email service is working correctly.
                </div>
                
                <p>Hello,</p>
                
                <p>This is a test email from <strong>Crown Mega Store</strong> to verify that your Resend email integration is working properly.</p>
                
                <p><strong>Email Configuration:</strong></p>
                <ul>
                    <li>Provider: Resend</li>
                    <li>Status: ✅ Active</li>
                    <li>From: onboarding@resend.dev (sandbox mode)</li>
                </ul>
                
                <p><strong>Next Steps:</strong></p>
                <ol>
                    <li>To send from your own domain (e.g., noreply@crownmegastore.com), you'll need to verify a custom domain in Resend</li>
                    <li>For now, you can use the sandbox mode for testing</li>
                    <li>In production, consider setting up a custom domain for better deliverability</li>
                </ol>
                
                <p>If you received this email, your email service is configured correctly! 🎉</p>
                
                <p>Best regards,<br>
                <strong>Crown Mega Store System</strong></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    print("\n📧 Sending test email...")
    print(f"To: {to_email}")
    print(f"Subject: {subject}")
    print("-" * 60)
    
    try:
        success = await EmailService.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content
        )
        
        if success:
            print("\n✅ SUCCESS! Email sent successfully via Resend!")
            print(f"Check your inbox at {to_email}")
            print("\nNote: Using onboarding@resend.dev (sandbox mode)")
            print("To use a custom domain:")
            print("1. Go to https://resend.com/domains")
            print("2. Add and verify your domain")
            print("3. Update the from_email in email_service.py")
        else:
            print("\n❌ FAILED! Email could not be sent.")
            print("Check the logs above for error details.")
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_resend_email())
