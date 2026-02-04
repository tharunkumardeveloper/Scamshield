"""
Request Inspector - Shows exactly what your API receives
This helps debug INVALID_REQUEST_BODY errors
"""
import requests
import json

VERCEL_URL = "https://scamshield-sable.vercel.app/api/honeypot"
API_KEY = "scamshield_2026_secure_key"

print("=" * 70)
print("REQUEST INSPECTOR - DEBUGGING INVALID_REQUEST_BODY")
print("=" * 70)
print()

# Test different request formats to find what works

test_cases = [
    {
        "name": "Standard Format",
        "payload": {
            "sessionId": "test-001",
            "message": {
                "sender": "scammer",
                "text": "Your account will be blocked",
                "timestamp": 1770005528731
            },
            "conversationHistory": []
        }
    },
    {
        "name": "With Empty Metadata",
        "payload": {
            "sessionId": "test-002",
            "message": {
                "sender": "scammer",
                "text": "Your account will be blocked",
                "timestamp": 1770005528731
            },
            "conversationHistory": [],
            "metadata": {}
        }
    },
    {
        "name": "With Full Metadata",
        "payload": {
            "sessionId": "test-003",
            "message": {
                "sender": "scammer",
                "text": "Your account will be blocked",
                "timestamp": 1770005528731
            },
            "conversationHistory": [],
            "metadata": {
                "channel": "SMS",
                "language": "English",
                "locale": "IN"
            }
        }
    },
    {
        "name": "With String Timestamp",
        "payload": {
            "sessionId": "test-004",
            "message": {
                "sender": "scammer",
                "text": "Your account will be blocked",
                "timestamp": "1770005528731"
            },
            "conversationHistory": []
        }
    },
    {
        "name": "Minimal (Only Required)",
        "payload": {
            "sessionId": "test-005",
            "message": {
                "text": "Your account will be blocked"
            }
        }
    },
    {
        "name": "With Previous History",
        "payload": {
            "sessionId": "test-006",
            "message": {
                "sender": "scammer",
                "text": "Send money now",
                "timestamp": 1770005528731
            },
            "conversationHistory": [
                {
                    "sender": "scammer",
                    "text": "Your account will be blocked",
                    "timestamp": 1770005528730
                },
                {
                    "sender": "user",
                    "text": "What should I do?",
                    "timestamp": 1770005528730
                }
            ]
        }
    }
]

results = []

for test in test_cases:
    print(f"Testing: {test['name']}")
    print("-" * 70)
    
    try:
        # Show request
        print("Request:")
        print(json.dumps(test['payload'], indent=2))
        print()
        
        # Send request
        response = requests.post(
            VERCEL_URL,
            json=test['payload'],
            headers={
                "Content-Type": "application/json",
                "x-api-key": API_KEY
            },
            timeout=10
        )
        
        # Show response
        print(f"Status: {response.status_code}")
        print("Response:")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text)
        
        # Record result
        result = {
            "test": test['name'],
            "status": response.status_code,
            "success": response.status_code == 200
        }
        results.append(result)
        
        if response.status_code == 200:
            print("✅ PASSED")
        else:
            print(f"❌ FAILED")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        results.append({
            "test": test['name'],
            "status": "ERROR",
            "success": False
        })
    
    print()
    print()

# Summary
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print()

for result in results:
    status_icon = "✅" if result['success'] else "❌"
    print(f"{status_icon} {result['test']}: {result['status']}")

print()
print("=" * 70)
print("ANALYSIS")
print("=" * 70)
print()

passed = sum(1 for r in results if r['success'])
total = len(results)

print(f"Passed: {passed}/{total}")
print()

if passed == total:
    print("✅ ALL TESTS PASSED!")
    print()
    print("Your API accepts all request formats correctly.")
    print("If GUVI tester shows INVALID_REQUEST_BODY, it's their bug.")
    print()
    print("Possible GUVI tester issues:")
    print("1. Tester sends malformed JSON")
    print("2. Tester uses wrong Content-Type header")
    print("3. Tester has JavaScript errors")
    print("4. Tester validation logic is broken")
    print()
    print("Solution: Contact GUVI support with these test results")
elif passed > 0:
    print(f"⚠️  PARTIAL SUCCESS ({passed}/{total})")
    print()
    print("Some formats work, others don't.")
    print("Check which formats failed and adjust your API.")
else:
    print("❌ ALL TESTS FAILED")
    print()
    print("Your API might have an issue. Check:")
    print("1. Is the API deployed and accessible?")
    print("2. Is the API key correct?")
    print("3. Are there any errors in Vercel logs?")

print()
print("Next steps:")
print("1. Check Vercel logs: https://vercel.com/dashboard")
print("2. Look for actual requests from GUVI tester")
print("3. Compare request format with what GUVI sends")
print("4. Contact GUVI support if no requests appear in logs")
