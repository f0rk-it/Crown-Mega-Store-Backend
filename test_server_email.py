#!/usr/bin/env python3
"""
Test email functionality on running server
Run this while your FastAPI server is running on localhost:8000
"""

import requests
import json
import sys
from datetime import datetime

def test_server_email():
    """Test email sending through the running server"""
    
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("TESTING EMAIL ON RUNNING SERVER")
    print("=" * 60)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/api/email-config", timeout=5)
        if response.status_code == 200:
            config = response.json()
            print("✅ Server is running and accessible")
            print(f"📧 Email Provider: {config.get('email_provider', 'Unknown')}")
            print(f"🔑 SendGrid API Key Set: {'✅ Yes' if config.get('sendgrid_config', {}).get('api_key_set') else '❌ No'}")
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Make sure your server is running with: python run.py")
        return False
    
    # Test 2: Send test email
    print(f"\n🧪 Sending test email via SendGrid...")
    
    # You can change this email to any email address you want to test with
    test_email = input("Enter your email for testing (or press Enter for business email): ").strip()
    if not test_email:
        test_email = "crownmegastore@gmail.com"  # Default to business email
    
    test_data = {
        "to_email": test_email,
        "test_message": f"Server email test sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/email-test",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=30  # Email sending might take a moment
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Test email sent successfully!")
                print(f"📬 Email sent to: {test_data['to_email']}")
                print("📱 Check your email inbox (may take 1-2 minutes)")
                
                # Show SMTP config for verification
                smtp_config = result.get("smtp_config", {})
                print(f"\n📋 Configuration used:")
                print(f"   Environment: {smtp_config.get('environment')}")
                print(f"   SMTP Host: {smtp_config.get('host')}")
                print(f"   SMTP Port: {smtp_config.get('port')}")
                
                return True
            else:
                print(f"❌ Email sending failed: {result.get('message')}")
                return False
        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - this might indicate email sending issues")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_order_email():
    """Test email through order creation"""
    
    print(f"\n🛒 Testing order creation email...")
    
    base_url = "http://localhost:8000"
    
    order_data = {
        "items": [
            {
                "product_id": "test-email-001",
                "product_name": "Email Test Product",
                "quantity": 1,
                "price": 99.99
            }
        ],
        "customer_info": {
            "name": "Email Test Customer",
            "email": "crownmegastore@gmail.com",
            "phone": "+1234567890",
            "delivery_address": "123 Email Test Street, Test City",
            "payment_preference": "bank_transfer",
            "order_notes": "This is a test order to verify SendGrid email integration"
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/orders/checkout",
            headers={"Content-Type": "application/json"},
            json=order_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Test order created successfully!")
                print(f"📦 Order ID: {result.get('order_id')}")
                print(f"💰 Total: ₦{result.get('total')}")
                print("📧 Order confirmation emails should be sent to:")
                print(f"   • Customer: {order_data['customer_info']['email']}")
                print(f"   • Business: crownmegastore@gmail.com")
                return True
            else:
                print(f"❌ Order creation failed: {result.get('message')}")
                return False
        else:
            print(f"❌ Order creation failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Order creation request failed: {e}")
        return False

def main():
    """Main test function"""
    
    print("🔍 This script tests email functionality on your running server")
    print("⚠️  Make sure your server is running: python run.py")
    print()
    
    # Test basic email functionality
    email_test_passed = test_server_email()
    
    if email_test_passed:
        # If basic test passed, try order email
        order_test_passed = test_order_email()
        
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS:")
        print(f"   📧 Email Test: {'✅ PASSED' if email_test_passed else '❌ FAILED'}")
        print(f"   🛒 Order Test: {'✅ PASSED' if order_test_passed else '❌ FAILED'}")
        
        if email_test_passed and order_test_passed:
            print("\n🎉 ALL TESTS PASSED!")
            print("Your SendGrid email integration is working perfectly!")
        else:
            print("\n⚠️  Some tests failed. Check your configuration.")
        print("=" * 60)
        
        return email_test_passed and order_test_passed
    else:
        print("\n❌ Basic email test failed. Skipping order test.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test script error: {e}")
        sys.exit(1)