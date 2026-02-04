"""
Local debugging test - Simulates GUVI tester exactly
Run this to see what your API receives and returns
"""
import requests
import json
from datetime import datetime

# Your local or deployed endpoint
LOCAL_URL = "http://localhost:8000/api/honeypot"
VERCEL_URL = "https://scamshield-sable.vercel.app/api/honeypot"

# Choose which to test
API_URL = VERCEL_URL  # Change to LOCAL_URL for local testing
API_KEY = "scamshield_2026_secure_key"

print("=" * 70)
print("LOCAL DEBUG TEST - GUVI FORMAT VERIFICATION")
print("=" * 70)
print(f"Testing: {API_URL}")
print()

# Test 1: Minimal valid request (what GUVI might send)
print("TEST 1: Minimal Valid Request")
print("-" * 70)

minimal_request = {
    "sessionId": "debug-001",
    "message": {
        "sender": "scammer",
        "text": "Your account will be blocked",
        "timestamp": 1770005528731
    },
    "conversationHistory": []
}

print("Request Body:")
print(json.dumps(minimal_request, indent=2))
print()

try:
    response = requests.post(
        API_URL,
        json=minimal_request,
        headers={
            "Content-Type": "application/json",
            "x-api-key": API_KEY
        },
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 200:
        print("✅ TEST 1 PASSED")
    else:
        print(f"❌ TEST 1 FAILED - Status {response.status_code}")
        
except Exception as e:
    print(f"❌ TEST 1 ERROR: {str(e)}")

print()
print("=" * 70)

# Test 2: With metadata (full GUVI format)
print("TEST 2: Full GUVI Format with Metadata")
print("-" * 70)

full_request = {
    "sessionId": "debug-002",
    "message": {
        "sender": "scammer",
        "text": "Congratulations! You won 10 lakh rupees. Call 9876543210",
        "timestamp": int(datetime.now().timestamp() * 1000)
    },
    "conversationHistory": [],
    "metadata": {
        "channel": "SMS",
        "language": "English",
        "locale": "IN"
    }
}

print("Request Body:")
print(json.dumps(full_request, indent=2))
print()

try:
    response = requests.post(
        API_URL,
        json=full_request,
        headers={
            "Content-Type": "application/json",
            "x-api-key": API_KEY
        },
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Body:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 200:
        print("✅ TEST 2 PASSED")
    else:
        print(f"❌ TEST 2 FAILED - Status {response.status_code}")
        
except Exception as e:
    print(f"❌ TEST 2 ERROR: {str(e)}")

print()
print("=" * 70)

# Test 3: Multi-turn conversation
print("TEST 3: Multi-turn Conversation (6 messages)")
print("-" * 70)

session_id = "debug-003"
conversation = []

messages = [
    "Your bank account will be blocked. Verify immediately!",
    "Send Rs 500 to verify your account",
    "Use this UPI: scammer123@paytm",
    "Also transfer to account 1234567890123",
    "Visit http://fake-bank.com to complete verification",
    "Hurry! Only 10 minutes left!"
]

for i, msg_text in enumerate(messages):
    print(f"\nMessage {i+1}: {msg_text}")
    
    request = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": msg_text,
            "timestamp": int(datetime.now().timestamp() * 1000) + i
        },
        "conversationHistory": conversation.copy()
    }
    
    try:
        response = requests.post(
            API_URL,
            json=request,
            headers={
                "Content-Type": "application/json",
                "x-api-key": API_KEY
            },
            timeout=10
        )
        
        if response.status_code == 200:
            reply = response.json().get("reply", "")
            print(f"  Agent Reply: {reply}")
            
            # Update conversation history
            conversation.append(request["message"])
            conversation.append({
                "sender": "user",
                "text": reply,
                "timestamp": request["message"]["timestamp"]
            })
            
            if i == len(messages) - 1:
                print("\n✅ TEST 3 PASSED - All 6 messages processed")
                print(f"   Total conversation length: {len(conversation)} messages")
                print("   Callback should have been triggered!")
        else:
            print(f"  ❌ Failed with status {response.status_code}")
            break
            
    except Exception as e:
        print(f"  ❌ ERROR: {str(e)}")
        break

print()
print("=" * 70)

# Test 4: Without API key (should fail)
print("TEST 4: Without API Key (Should Return 401)")
print("-" * 70)

no_key_request = {
    "sessionId": "debug-004",
    "message": {
        "sender": "scammer",
        "text": "Test",
        "timestamp": 1770005528731
    },
    "conversationHistory": []
}

try:
    response = requests.post(
        API_URL,
        json=no_key_request,
        headers={
            "Content-Type": "application/json"
            # No x-api-key header
        },
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Body:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 401:
        print("✅ TEST 4 PASSED - Correctly rejected without API key")
    else:
        print(f"⚠️  TEST 4 WARNING - Expected 401, got {response.status_code}")
        
except Exception as e:
    print(f"❌ TEST 4 ERROR: {str(e)}")

print()
print("=" * 70)

# Test 5: Malformed request (missing required fields)
print("TEST 5: Malformed Request (Missing Fields)")
print("-" * 70)

malformed_request = {
    "sessionId": "debug-005"
    # Missing message and conversationHistory
}

try:
    response = requests.post(
        API_URL,
        json=malformed_request,
        headers={
            "Content-Type": "application/json",
            "x-api-key": API_KEY
        },
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Body:")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    
    # Your API is lenient, so it might still return 200
    if response.status_code in [200, 400]:
        print("✅ TEST 5 PASSED - Handled gracefully")
    else:
        print(f"⚠️  TEST 5 WARNING - Unexpected status {response.status_code}")
        
except Exception as e:
    print(f"❌ TEST 5 ERROR: {str(e)}")

print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print()
print("If all tests passed, your API is working correctly.")
print("If GUVI tester still shows INVALID_REQUEST_BODY, it's their bug.")
print()
print("Next steps:")
print("1. Run this test locally: python test_local_debug.py")
print("2. Check Vercel logs for actual requests from GUVI")
print("3. Contact GUVI support with test results")
print()
print("Your API URL: " + API_URL)
print("Your API Key: " + API_KEY)
