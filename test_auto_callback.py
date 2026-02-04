import requests
import json
import time

# Test if API automatically sends callback after 6 messages

API_URL = "https://scamshield-sable.vercel.app/api/honeypot"
API_KEY = "scamshield_2026_secure_key"

print("=" * 70)
print("TESTING AUTOMATIC CALLBACK (API should send after 6 messages)")
print("=" * 70)

session_id = f"auto-callback-test-{int(time.time())}"
conversation_history = []

messages = [
    "Your account will be blocked",
    "Send money to verify@paytm",
    "Share your account number",
    "Click http://fake.com",
    "Transfer ₹500 now",
    "Urgent! Do it immediately",
    "Last warning!"
]

for i, msg in enumerate(messages):
    print(f"\n--- Message {i+1} ---")
    
    payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": msg,
            "timestamp": int(time.time() * 1000)
        },
        "conversationHistory": conversation_history.copy(),
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    response = requests.post(API_URL, json=payload, headers={"x-api-key": API_KEY})
    
    if response.status_code == 200:
        result = response.json()
        print(f"Scammer: {msg}")
        print(f"Agent: {result['reply']}")
        
        # Update history
        conversation_history.append({"sender": "scammer", "text": msg, "timestamp": int(time.time() * 1000)})
        conversation_history.append({"sender": "user", "text": result['reply'], "timestamp": int(time.time() * 1000)})
        
        if len(conversation_history) == 6:
            print("\n🎯 Reached 6 messages - API should trigger callback now!")
    else:
        print(f"Error: {response.status_code}")
    
    time.sleep(1)

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
print(f"\nTotal messages: {len(conversation_history)}")
print("Check Vercel logs to see if callback was sent automatically!")
print(f"Session ID: {session_id}")
