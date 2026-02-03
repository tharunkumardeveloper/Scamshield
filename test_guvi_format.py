"""
Test script to verify GUVI platform request format
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000/api/honeypot")
API_KEY = os.getenv("API_KEY", "your-secret-key")

def test_guvi_format():
    """Test with exact GUVI format"""
    print("Testing GUVI Platform Format")
    print("=" * 60)
    
    # Exact format from GUVI documentation
    payload = {
        "sessionId": "test-guvi-001",
        "message": {
            "sender": "scammer",
            "text": "URGENT: Your SBI account has been compromised. Your account will be blocked in 2 hours. Share your account number and OTP immediately to verify your identity.",
            "timestamp": 1770005528731
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    print(f"\nAPI URL: {API_URL}")
    print(f"API Key: {API_KEY[:10]}...")
    print(f"\nRequest Payload:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"\nResponse Body:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success" and "reply" in result:
                print("\n✅ SUCCESS! API is working correctly")
                print(f"Agent Reply: {result['reply']}")
                return True
            else:
                print("\n❌ FAILED! Response format incorrect")
                return False
        else:
            print(f"\n❌ FAILED! Status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

def test_missing_fields():
    """Test with missing required fields"""
    print("\n\nTesting Missing Fields (Should Return 400)")
    print("=" * 60)
    
    # Missing sessionId
    payload = {
        "message": {
            "sender": "scammer",
            "text": "Test message",
            "timestamp": 1770005528731
        },
        "conversationHistory": []
    }
    
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        print(f"Response Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 400:
            print("\n✅ Correctly rejected invalid request")
        else:
            print("\n⚠️  Should have returned 400")
            
    except Exception as e:
        print(f"Error: {str(e)}")

def test_invalid_api_key():
    """Test with invalid API key"""
    print("\n\nTesting Invalid API Key (Should Return 401)")
    print("=" * 60)
    
    payload = {
        "sessionId": "test-001",
        "message": {
            "sender": "scammer",
            "text": "Test",
            "timestamp": 1770005528731
        },
        "conversationHistory": []
    }
    
    headers = {
        "x-api-key": "wrong-key",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        print(f"Response Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 401:
            print("\n✅ Correctly rejected invalid API key")
        else:
            print("\n⚠️  Should have returned 401")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    print("\n🔍 GUVI Platform Format Validation Test\n")
    
    # Test 1: Valid request
    success = test_guvi_format()
    
    # Test 2: Missing fields
    test_missing_fields()
    
    # Test 3: Invalid API key
    test_invalid_api_key()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Your API is ready for GUVI platform!")
    else:
        print("❌ Fix the issues above before submitting")
    print("=" * 60 + "\n")
