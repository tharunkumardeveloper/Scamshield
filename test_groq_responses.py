import requests
import json
import time

# Test if Groq AI is generating dynamic responses

API_URL = "https://scamshield-sable.vercel.app/api/honeypot"
API_KEY = "scamshield_2026_secure_key"

print("=" * 70)
print("TESTING GROQ AI DYNAMIC RESPONSES")
print("=" * 70)

session_id = f"groq-test-{int(time.time())}"
conversation_history = []

# Different types of scam messages
messages = [
    "URGENT: Your SBI account will be blocked in 2 hours!",
    "You need to verify your identity immediately.",
    "Share your account number and OTP with me.",
    "Send ₹500 to verify@paytm to unblock your account.",
    "Why are you not responding? This is urgent!"
]

print("\n🤖 Testing if responses are dynamic (not predefined)...\n")

responses_received = []

for i, msg in enumerate(messages):
    print(f"--- Turn {i+1} ---")
    
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
    
    response = requests.post(API_URL, json=payload, headers={"x-api-key": API_KEY}, timeout=10)
    
    if response.status_code == 200:
        result = response.json()
        reply = result['reply']
        
        print(f"Scammer: {msg}")
        print(f"Agent: {reply}")
        print()
        
        responses_received.append(reply)
        
        # Update history
        conversation_history.append({"sender": "scammer", "text": msg, "timestamp": int(time.time() * 1000)})
        conversation_history.append({"sender": "user", "text": reply, "timestamp": int(time.time() * 1000)})
    else:
        print(f"Error: {response.status_code}")
        break
    
    time.sleep(2)

print("\n" + "=" * 70)
print("ANALYSIS")
print("=" * 70)

# Check if responses are varied (not all the same)
unique_responses = len(set(responses_received))
total_responses = len(responses_received)

print(f"\nTotal responses: {total_responses}")
print(f"Unique responses: {unique_responses}")

if unique_responses == total_responses:
    print("\n✅ EXCELLENT! All responses are unique - Groq AI is working!")
elif unique_responses >= total_responses * 0.8:
    print("\n✅ GOOD! Most responses are unique - Groq AI is working!")
else:
    print("\n⚠️ WARNING: Many repeated responses - Groq might not be configured")
    print("   Make sure GROQ_API_KEY is set in Vercel environment variables!")

print("\nResponses received:")
for i, resp in enumerate(responses_received, 1):
    print(f"{i}. {resp}")
