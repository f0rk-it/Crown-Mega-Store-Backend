#!/usr/bin/env python3
"""
SendGrid Email Test Script
Run this to test SendGrid email functionality specifically
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.email_service import EmailService
from app.core.config import settings


async def test_sendgrid_email():
    """Test SendGrid email configuration"""
    print("=" * 60)
    print("CROWN MEGA STORE - SENDGRID EMAIL TEST")
    print("=" * 60)
    
    # Check SendGrid configuration
    print("\n📧 SendGrid Configuration:")
    print(f"Email Provider: {settings.EMAIL_PROVIDER}")
    print(f"From Email: {settings.FROM_EMAIL}")
    print(f"SendGrid API Key Set: {'✅ Yes' if settings.SENDGRID_API_KEY else '❌ No'}")
    if settings.SENDGRID_API_KEY:
        print(f"API Key Preview: {settings.SENDGRID_API_KEY[:10]}...")
    
    # Check if SendGrid is available
    try:
        from sendgrid import SendGridAPIClient
        print("✅ SendGrid package is available")
    except ImportError:
        print("❌ SendGrid package not installed")
        return False
    
    if not settings.SENDGRID_API_KEY:
        print("\n❌ SendGrid API Key is not configured")
        return False
    
    print("\n✅ All SendGrid configurations are present")
    
    # Test email sending
    print("\n🧪 Testing SendGrid email sending...")
    
    # You can change this to any email address you want to test with
    test_email = input("Enter your email address for testing (or press Enter for business email): ").strip()
    if not test_email:
        test_email = settings.BUSINESS_EMAIL  # Default to business email
    
    test_html = """
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <div style="max-width: 500px; margin: 0 auto;">
            <div style="background: #e74c3c; color: white; padding: 15px; border-radius: 5px;">
                <h2>🚀 SendGrid Test Successful!</h2>
            </div>
            <div style="padding: 20px; background: #f9f9f9; margin-top: 10px; border-radius: 5px;">
                <p><strong>Great news!</strong> Your SendGrid integration is working perfectly!</p>
                <p>This test email was sent using SendGrid API from your Crown Mega Store backend.</p>
                <p><strong>Environment:</strong> {}</p>
                <p><strong>From Email:</strong> {}</p>
                <p><strong>Provider:</strong> SendGrid</p>
            </div>
        </div>
    </body>
    </html>
    """.format(settings.ENVIRONMENT, settings.FROM_EMAIL)
    
    try:
        # Test SendGrid directly
        print("Testing direct SendGrid sending...")
        success = await EmailService.send_email_via_sendgrid(
            to_email=test_email,
            subject="🚀 SendGrid Integration Test - Crown Mega Store",
            html_content=test_html
        )
        
        if success:
            print(f"✅ SendGrid test email sent successfully to {test_email}")
            print("📱 Check your email inbox (may take a few moments)")
            
            # Also test the main send_email method
            print("\nTesting main email service with SendGrid provider...")
            success2 = await EmailService.send_email(
                to_email=test_email,
                subject="📧 Email Service Test via SendGrid - Crown Mega Store",
                html_content=test_html
            )
            
            if success2:
                print("✅ Main email service with SendGrid provider also works!")
                return True
            else:
                print("❌ Main email service failed")
                return False
        else:
            print("❌ SendGrid test email failed to send")
            return False
            
    except Exception as e:
        print(f"❌ SendGrid test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    try:
        result = asyncio.run(test_sendgrid_email())
        
        print("\n" + "=" * 60)
        if result:
            print("🎉 SENDGRID EMAIL TEST PASSED!")
            print("Your SendGrid integration is working correctly!")
            print("Emails will now be sent via SendGrid API.")
        else:
            print("❌ SENDGRID EMAIL TEST FAILED!")
            print("Please check your SendGrid API key and configuration.")
        print("=" * 60)
        
        return 0 if result else 1
        
    except Exception as e:
        print(f"\n❌ Test script failed: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)