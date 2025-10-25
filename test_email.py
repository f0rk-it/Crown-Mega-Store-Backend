#!/usr/bin/env python3
"""
Email Configuration Test Script
Run this script to test email settings before deployment
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.email_service import EmailService
from app.core.config import settings


async def test_email_config():
    """Test email configuration"""
    print("=" * 60)
    print("CROWN MEGA STORE - EMAIL CONFIGURATION TEST")
    print("=" * 60)
    
    # Check configuration
    print("\n📧 Email Configuration:")
    print(f"SMTP Host: {settings.SMTP_HOST}")
    print(f"SMTP Port: {settings.SMTP_PORT}")
    print(f"SMTP User: {settings.SMTP_USER}")
    print(f"Business Email: {settings.BUSINESS_EMAIL}")
    print(f"Password Set: {'✅ Yes' if settings.SMTP_PASSWORD else '❌ No'}")
    print(f"Password Length: {len(settings.SMTP_PASSWORD) if settings.SMTP_PASSWORD else 0} characters")
    
    # Check if all required settings are present
    missing_configs = []
    if not settings.SMTP_HOST:
        missing_configs.append("SMTP_HOST")
    if not settings.SMTP_PORT:
        missing_configs.append("SMTP_PORT")
    if not settings.SMTP_USER:
        missing_configs.append("SMTP_USER")
    if not settings.SMTP_PASSWORD:
        missing_configs.append("SMTP_PASSWORD")
    if not settings.BUSINESS_EMAIL:
        missing_configs.append("BUSINESS_EMAIL")
    
    if missing_configs:
        print(f"\n❌ Missing configurations: {', '.join(missing_configs)}")
        return False
    
    print("\n✅ All email configurations are present")
    
    # Test email sending
    print("\n🧪 Testing email sending...")
    test_email = settings.BUSINESS_EMAIL  # Send test email to business email
    
    test_html = """
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <div style="max-width: 500px; margin: 0 auto;">
            <div style="background: #27ae60; color: white; padding: 15px; border-radius: 5px;">
                <h2>✅ Email Test Successful!</h2>
            </div>
            <div style="padding: 20px; background: #f9f9f9; margin-top: 10px; border-radius: 5px;">
                <p><strong>Congratulations!</strong> Your email service is working correctly.</p>
                <p>This test email was sent from your Crown Mega Store API.</p>
                <p><strong>Environment:</strong> {}</p>
            </div>
        </div>
    </body>
    </html>
    """.format(settings.ENVIRONMENT)
    
    try:
        success = await EmailService.send_email(
            to_email=test_email,
            subject="✅ Email Configuration Test - Crown Mega Store API",
            html_content=test_html
        )
        
        if success:
            print(f"✅ Test email sent successfully to {test_email}")
            print("📱 Check your email inbox/spam folder")
            return True
        else:
            print("❌ Test email failed to send")
            return False
            
    except Exception as e:
        print(f"❌ Email test failed with error: {str(e)}")
        return False


def main():
    """Main test function"""
    try:
        result = asyncio.run(test_email_config())
        
        print("\n" + "=" * 60)
        if result:
            print("🎉 EMAIL SERVICE TEST PASSED!")
            print("Your email service should work correctly on Render.")
        else:
            print("❌ EMAIL SERVICE TEST FAILED!")
            print("Please check your configuration and try again.")
        print("=" * 60)
        
        return 0 if result else 1
        
    except Exception as e:
        print(f"\n❌ Test script failed: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)