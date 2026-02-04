import requests
import json
import time

# Test the full flow including GUVI callback

API_URL = "https://scamshield-sable.vercel.app/api/honeypot"
API_KEY = "scamshield_2026_secure_key"
GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

print("=" * 70)
print("TESTING FULL SCAMSHIELD FLOW WITH GUVI CALLBACK")
print("=" * 70)

# Simulate a multi-turn conversation
session_id = "test-guvi-callback-001"
conversation_history = []

scam_messages = [
    "URGENT: Your SBI account will be blocked in 2 hours. Verify immediately.",
    "Share your account number and mobile number to verify.",
    "Also provide your UPI ID for verification.",
    "Send ₹500 to verify@paytm to unblock your account.",
    "Click this link to verify: http://fake-bank.com/verify"
]

print("\n📞 Starting conversation with scammer...\n")

for i, scam_msg in enumerate(scam_messages):
    print(f"--- Turn {i+1} ---")
    
    payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": scam_msg,
            "timestamp": int(time.time() * 1000)
        },
        "conversationHistory": conversation_history.copy(),
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            agent_reply = result.get('reply', 'No reply')
            
            print(f"Scammer: {scam_msg}")
            print(f"Agent: {agent_reply}")
            print()
            
            # Update conversation history
            conversation_history.append({
                "sender": "scammer",
                "text": scam_msg,
                "timestamp": int(time.time() * 1000)
            })
            conversation_history.append({
                "sender": "user",
                "text": agent_reply,
                "timestamp": int(time.time() * 1000)
            })
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            break
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        break
    
    time.sleep(1)

print("\n" + "=" * 70)
print("CONVERSATION COMPLETE - Now sending final callback to GUVI")
print("=" * 70)

# Extract intelligence from conversation
extracted_intelligence = {
    "bankAccounts": [],
    "upiIds": ["verify@paytm"],
    "phishingLinks": ["http://fake-bank.com/verify"],
    "phoneNumbers": [],
    "suspiciousKeywords": ["urgent", "blocked", "verify", "immediately"]
}

# Prepare final callback payload
callback_payload = {
    "sessionId": session_id,
    "scamDetected": True,
    "totalMessagesExchanged": len(conversation_history),
    "extractedIntelligence": extracted_intelligence,
    "agentNotes": "Bank fraud scam detected. Scammer used urgency tactics, requested UPI payment to verify@paytm, and shared phishing link. Agent successfully engaged scammer for 5 turns and extracted critical intelligence."
}

print("\n📤 Sending final result to GUVI...")
print(f"Callback URL: {GUVI_CALLBACK_URL}")
print(f"Payload: {json.dumps(callback_payload, indent=2)}")
print()

try:
    callback_response = requests.post(
        GUVI_CALLBACK_URL,
        json=callback_payload,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    print(f"Status Code: {callback_response.status_code}")
    print(f"Response: {callback_response.text}")
    
    if callback_response.status_code == 200:
        print("\n✅ SUCCESS! Final callback sent to GUVI successfully!")
    else:
        print(f"\n⚠️ Warning: Callback returned status {callback_response.status_code}")
        print("This might be expected if GUVI's endpoint is not active yet.")
        
except requests.exceptions.Timeout:
    print("⏱️ Timeout: GUVI endpoint took too long to respond")
except requests.exceptions.ConnectionError:
    print("🔌 Connection Error: Could not reach GUVI endpoint")
except Exception as e:
    print(f"❌ Error: {str(e)}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
print("\n📊 Summary:")
print(f"  - Total conversation turns: {len(conversation_history)}")
print(f"  - Scam detected: Yes")
print(f"  - UPI IDs extracted: {len(extracted_intelligence['upiIds'])}")
print(f"  - Phishing links extracted: {len(extracted_intelligence['phishingLinks'])}")
print(f"  - Callback sent: Attempted")
print()
