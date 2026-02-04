import requests
import json
import time
import random

# Custom tester to verify Vercel logs are updating

API_URL = "https://scamshield-sable.vercel.app/api/honeypot"
API_KEY = "scamshield_2026_secure_key"

print("=" * 80)
print("CUSTOM VERCEL LOGS TESTER")
print("=" * 80)
print("\nThis test will send requests to your API and you can verify")
print("that Vercel logs are updating with [REQUEST] and [RESPONSE] tags.\n")
print("After running this test:")
print("1. Go to https://vercel.com/dashboard")
print("2. Click on your project")
print("3. Click 'Logs' tab")
print("4. Look for [REQUEST] and [RESPONSE] logs")
print("=" * 80)

# Generate unique session ID so you can find it in logs
test_id = f"VERCEL-LOG-TEST-{int(time.time())}"
print(f"\n🔍 Test Session ID: {test_id}")
print("   (Search for this in Vercel logs to find your test)\n")

# Test 1: Simple request
print("=" * 80)
print("TEST 1: Simple Bank Fraud Message")
print("=" * 80)

payload1 = {
    "sessionId": test_id,
    "message": {
        "sender": "scammer",
        "text": "URGENT: Your SBI account will be blocked in 2 hours!",
        "timestamp": int(time.time() * 1000)
    },
    "conversationHistory": [],
    "metadata": {
        "channel": "SMS",
        "language": "English",
        "locale": "IN"
    }
}

print(f"\n📤 Sending request...")
print(f"URL: {API_URL}")
print(f"Session ID: {test_id}")
print(f"Message: {payload1['message']['text']}")

try:
    response1 = requests.post(
        API_URL,
        json=payload1,
        headers={
            "Content-Type": "application/json",
            "x-api-key": API_KEY
        },
        timeout=10
    )
    
    print(f"\n✅ Response received!")
    print(f"Status Code: {response1.status_code}")
    print(f"Response: {json.dumps(response1.json(), indent=2)}")
    
    if response1.status_code == 200:
        print("\n✅ TEST 1 PASSED")
    else:
        print(f"\n❌ TEST 1 FAILED - Status {response1.status_code}")
        
except Exception as e:
    print(f"\n❌ TEST 1 FAILED - Error: {str(e)}")

time.sleep(2)

# Test 2: Follow-up message
print("\n" + "=" * 80)
print("TEST 2: Follow-up UPI Request")
print("=" * 80)

payload2 = {
    "sessionId": test_id,
    "message": {
        "sender": "scammer",
        "text": "Send ₹500 to verify@paytm immediately to unblock your account",
        "timestamp": int(time.time() * 1000)
    },
    "conversationHistory": [
        {
            "sender": "scammer",
            "text": "URGENT: Your SBI account will be blocked in 2 hours!",
            "timestamp": int(time.time() * 1000) - 5000
        },
        {
            "sender": "user",
            "text": "Oh no, what should I do?",
            "timestamp": int(time.time() * 1000) - 3000
        }
    ],
    "metadata": {
        "channel": "SMS",
        "language": "English",
        "locale": "IN"
    }
}

print(f"\n📤 Sending follow-up request...")
print(f"Message: {payload2['message']['text']}")

try:
    response2 = requests.post(
        API_URL,
        json=payload2,
        headers={
            "Content-Type": "application/json",
            "x-api-key": API_KEY
        },
        timeout=10
    )
    
    print(f"\n✅ Response received!")
    print(f"Status Code: {response2.status_code}")
    print(f"Response: {json.dumps(response2.json(), indent=2)}")
    
    if response2.status_code == 200:
        print("\n✅ TEST 2 PASSED")
    else:
        print(f"\n❌ TEST 2 FAILED - Status {response2.status_code}")
        
except Exception as e:
    print(f"\n❌ TEST 2 FAILED - Error: {str(e)}")

time.sleep(2)

# Test 3: Invalid API key (should fail)
print("\n" + "=" * 80)
print("TEST 3: Invalid API Key (Should Return 401)")
print("=" * 80)

print(f"\n📤 Sending request with wrong API key...")

try:
    response3 = requests.post(
        API_URL,
        json=payload1,
        headers={
            "Content-Type": "application/json",
            "x-api-key": "wrong-key-12345"
        },
        timeout=10
    )
    
    print(f"\n✅ Response received!")
    print(f"Status Code: {response3.status_code}")
    print(f"Response: {json.dumps(response3.json(), indent=2)}")
    
    if response3.status_code == 401:
        print("\n✅ TEST 3 PASSED - Correctly rejected invalid key")
    else:
        print(f"\n⚠️ TEST 3 WARNING - Expected 401, got {response3.status_code}")
        
except Exception as e:
    print(f"\n❌ TEST 3 FAILED - Error: {str(e)}")

time.sleep(2)

# Test 4: Malformed JSON (should handle gracefully)
print("\n" + "=" * 80)
print("TEST 4: Missing Required Fields (Should Handle Gracefully)")
print("=" * 80)

payload4 = {
    "sessionId": test_id,
    "message": {
        "text": "Test message"
        # Missing sender and timestamp
    }
}

print(f"\n📤 Sending request with missing fields...")

try:
    response4 = requests.post(
        API_URL,
        json=payload4,
        headers={
            "Content-Type": "application/json",
            "x-api-key": API_KEY
        },
        timeout=10
    )
    
    print(f"\n✅ Response received!")
    print(f"Status Code: {response4.status_code}")
    print(f"Response: {json.dumps(response4.json(), indent=2)}")
    
    if response4.status_code == 200:
        print("\n✅ TEST 4 PASSED - Handled gracefully")
    else:
        print(f"\n⚠️ TEST 4 WARNING - Status {response4.status_code}")
        
except Exception as e:
    print(f"\n❌ TEST 4 FAILED - Error: {str(e)}")

# Final summary
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)

print(f"\n🔍 Your Test Session ID: {test_id}")
print("\n📋 Next Steps:")
print("1. Go to: https://vercel.com/dashboard")
print("2. Click on your project: scamshield-sable")
print("3. Click on 'Logs' tab")
print(f"4. Search for: {test_id}")
print("5. Look for logs with [REQUEST] and [RESPONSE] tags")
print("\n✅ If you see logs with your session ID, Vercel logging is working!")
print("❌ If you DON'T see logs, there might be a deployment issue")

print("\n" + "=" * 80)
print("WHAT TO LOOK FOR IN VERCEL LOGS:")
print("=" * 80)
print("""
You should see logs like:

[REQUEST] Headers: {...}
[REQUEST] Raw body: {"sessionId":"VERCEL-LOG-TEST-...","message":{...}}
[REQUEST] Parsed JSON: {...}
[RESPONSE] Session: VERCEL-LOG-TEST-..., Scam: bank_fraud, Reply: ...

If you see these, your API is working perfectly!
If you DON'T see these, the deployment might not have the latest code.
""")

print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)
