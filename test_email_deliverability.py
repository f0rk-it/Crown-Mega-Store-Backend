"""
Test script for improved email deliverability
Run this to test the new email formats and check spam scores
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.email_service import EmailService
from app.core.config import get_settings

settings = get_settings()

# Sample order data for testing
SAMPLE_ORDER_DATA = {
    'order_id': 'TEST-001',
    'total': 25000.00,
    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'customer_info': {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'phone': '+234-801-234-5678',
        'delivery_address': '123 Test Street, Lagos, Nigeria',
        'pickup_preference': False,
        'payment_preference': 'Bank Transfer',
        'order_notes': 'Please handle with care'
    },
    'items': [
        {
            'product_name': 'Samsung Galaxy S24',
            'quantity': 1,
            'price': 800000.00
        },
        {
            'product_name': 'iPhone 15 Pro',
            'quantity': 1,
            'price': 1200000.00
        }
    ]
}

async def test_customer_email():
    """Test customer confirmation email"""
    print("🧪 Testing Customer Confirmation Email...")
    
    html_content = EmailService.format_order_email_customer(SAMPLE_ORDER_DATA)
    
    # Save to file for inspection
    with open('test_customer_email.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Customer email HTML saved to 'test_customer_email.html'")
    
    # Optionally send test email
    test_email = input("Enter test email address (or press Enter to skip sending): ").strip()
    if test_email:
        subject = f"Test: Order Confirmation - #{SAMPLE_ORDER_DATA['order_id']}"
        success = await EmailService.send_email(test_email, subject, html_content)
        if success:
            print(f"✅ Test email sent successfully to {test_email}")
        else:
            print(f"❌ Failed to send test email to {test_email}")
    
    return html_content

async def test_business_email():
    """Test business notification email"""
    print("\n🧪 Testing Business Notification Email...")
    
    html_content = EmailService.format_order_email_business(SAMPLE_ORDER_DATA)
    
    # Save to file for inspection
    with open('test_business_email.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Business email HTML saved to 'test_business_email.html'")
    
    # Optionally send test email
    test_email = input("Enter business test email address (or press Enter to skip sending): ").strip()
    if test_email:
        subject = f"New Order Notification - #{SAMPLE_ORDER_DATA['order_id']}"
        success = await EmailService.send_email(test_email, subject, html_content)
        if success:
            print(f"✅ Test email sent successfully to {test_email}")
        else:
            print(f"❌ Failed to send test email to {test_email}")
    
    return html_content

async def test_status_update_email():
    """Test status update email"""
    print("\n🧪 Testing Status Update Email...")
    
    order_data = {
        'order_id': SAMPLE_ORDER_DATA['order_id'],
        'customer_name': SAMPLE_ORDER_DATA['customer_info']['name'],
        'total': SAMPLE_ORDER_DATA['total']
    }
    
    subject, html_content = EmailService.format_status_update_email(
        order_data, 
        'confirmed', 
        'Your payment details will be sent shortly.'
    )
    
    # Save to file for inspection
    with open('test_status_update_email.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Status update email HTML saved to 'test_status_update_email.html'")
    print(f"📧 Subject: {subject}")
    
    # Optionally send test email
    test_email = input("Enter test email address for status update (or press Enter to skip): ").strip()
    if test_email:
        success = await EmailService.send_email(test_email, subject, html_content)
        if success:
            print(f"✅ Test email sent successfully to {test_email}")
        else:
            print(f"❌ Failed to send test email to {test_email}")
    
    return html_content

def analyze_email_content(html_content, email_type):
    """Basic analysis of email content for spam indicators"""
    print(f"\n📊 Analysis for {email_type} email:")
    
    # Count various elements
    char_count = len(html_content)
    word_count = len(html_content.split())
    
    # Check for potential spam indicators
    spam_words = ['free', 'urgent', 'act now', 'limited time', 'guarantee', 'no obligation']
    found_spam_words = [word for word in spam_words if word.lower() in html_content.lower()]
    
    # Count exclamation marks
    exclamation_count = html_content.count('!')
    
    # Check for all caps (more than 20% of words)
    words = html_content.split()
    caps_words = [word for word in words if word.isupper() and len(word) > 2]
    caps_percentage = (len(caps_words) / len(words)) * 100 if words else 0
    
    print(f"  📏 Character count: {char_count:,}")
    print(f"  📝 Word count: {word_count:,}")
    print(f"  ❗ Exclamation marks: {exclamation_count}")
    print(f"  🔤 ALL CAPS percentage: {caps_percentage:.1f}%")
    
    if found_spam_words:
        print(f"  ⚠️  Potential spam words found: {', '.join(found_spam_words)}")
    else:
        print(f"  ✅ No obvious spam words detected")
    
    # Email client compatibility check
    if 'DOCTYPE html PUBLIC' in html_content:
        print(f"  ✅ Uses email-compatible DOCTYPE")
    else:
        print(f"  ❌ Missing email-compatible DOCTYPE")
    
    if 'table' in html_content.lower():
        print(f"  ✅ Uses table-based layout (email client friendly)")
    else:
        print(f"  ❌ May not use table-based layout")

async def main():
    """Main test function"""
    print("🚀 Crown Mega Store Email Deliverability Test")
    print("=" * 50)
    
    try:
        # Test all email types
        customer_html = await test_customer_email()
        business_html = await test_business_email()
        status_html = await test_status_update_email()
        
        # Analyze content
        print("\n" + "=" * 50)
        print("📊 EMAIL CONTENT ANALYSIS")
        print("=" * 50)
        
        analyze_email_content(customer_html, "Customer Confirmation")
        analyze_email_content(business_html, "Business Notification")
        analyze_email_content(status_html, "Status Update")
        
        print("\n" + "=" * 50)
        print("🎯 NEXT STEPS FOR TESTING:")
        print("=" * 50)
        print("1. 📧 Send test emails to check@mail-tester.com to get spam scores")
        print("2. 🔍 Open the generated HTML files in different email clients")
        print("3. 📱 Test on mobile devices (Gmail app, Outlook mobile, etc.)")
        print("4. 📊 Monitor delivery rates and engagement metrics")
        print("5. 🛡️ Set up SPF, DKIM, and DMARC records (see EMAIL_DELIVERABILITY_GUIDE.md)")
        
        print(f"\n✅ All tests completed successfully!")
        print(f"📁 Generated files:")
        print(f"   - test_customer_email.html")
        print(f"   - test_business_email.html") 
        print(f"   - test_status_update_email.html")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        print(f"💡 Make sure your .env file is configured correctly")

if __name__ == "__main__":
    print("Starting email deliverability tests...")
    asyncio.run(main())