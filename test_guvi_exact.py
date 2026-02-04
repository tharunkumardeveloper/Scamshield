import requests
import json

# Test with EXACT GUVI format
url = "https://scamshield-sable.vercel.app/api/honeypot"

# Exact format from GUVI docs
payload = {
    "sessionId": "wertyu-dfghj-ertyui",
    "message": {
        "sender": "scammer",
        "text": "Your bank account will be blocked today. Verify immediately.",
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
    "Content-Type": "application/json",
    "x-api-key": "scamshield_2026_secure_key"
}

print("Testing with EXACT GUVI format...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print("\nSending request...\n")

response = requests.post(url, json=payload, headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

if response.status_code == 200:
    print("\n✅ SUCCESS! Your API is working correctly!")
else:
    print(f"\n❌ ERROR: {response.status_code}")
