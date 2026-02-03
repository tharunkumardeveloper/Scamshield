import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Test configuration
API_URL = os.getenv("API_URL", "http://localhost:8000/api/honeypot")
API_KEY = os.getenv("API_KEY", "your-secret-key")

def test_first_message():
    """Test with first scam message"""
    print("=" * 60)
    print("TEST 1: First Message (Bank Scam)")
    print("=" * 60)
    
    payload = {
        "sessionId": "test-session-001",
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
    
    response = requests.post(API_URL, json=payload, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    
    return response.json()

def test_follow_up_message():
    """Test with follow-up message"""
    print("=" * 60)
    print("TEST 2: Follow-up Message")
    print("=" * 60)
    
    payload = {
        "sessionId": "test-session-002",
        "message": {
            "sender": "scammer",
            "text": "Share your UPI ID to avoid account suspension. Send to scammer@paytm immediately.",
            "timestamp": 1770005528731
        },
        "conversationHistory": [
            {
                "sender": "scammer",
                "text": "Your bank account will be blocked today. Verify immediately.",
                "timestamp": 1770005528731
            },
            {
                "sender": "user",
                "text": "Why will my account be blocked?",
                "timestamp": 1770005528731
            }
        ],
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
    
    response = requests.post(API_URL, json=payload, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    
    return response.json()

def test_multi_turn_conversation():
    """Test a multi-turn conversation to trigger final callback"""
    print("=" * 60)
    print("TEST 3: Multi-turn Conversation (Should trigger callback)")
    print("=" * 60)
    
    session_id = "test-session-003"
    conversation = []
    
    messages = [
        "Your account will be blocked. Verify now!",
        "Send money to 9876543210@paytm to unblock",
        "Also share your bank account number",
        "Transfer ₹500 to account 1234567890123",
        "Click this link: http://fake-bank.com/verify"
    ]
    
    for i, scam_msg in enumerate(messages):
        print(f"\n--- Turn {i+1} ---")
        
        payload = {
            "sessionId": session_id,
            "message": {
                "sender": "scammer",
                "text": scam_msg,
                "timestamp": 1770005528731 + (i * 1000)
            },
            "conversationHistory": conversation.copy(),
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
        
        response = requests.post(API_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Scammer: {scam_msg}")
            print(f"Agent: {result.get('reply', 'No reply')}")
            
            # Update conversation history
            conversation.append({
                "sender": "scammer",
                "text": scam_msg,
                "timestamp": 1770005528731 + (i * 1000)
            })
            conversation.append({
                "sender": "user",
                "text": result.get('reply', ''),
                "timestamp": 1770005528731 + (i * 1000) + 500
            })
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            break
    
    print("\n" + "=" * 60)
    print("Multi-turn test completed!")
    print("Check logs to see if final callback was sent to GUVI")
    print("=" * 60)

if __name__ == "__main__":
    print("\n🔍 Testing ScamShield Honeypot API\n")
    
    try:
        # Test 1: First message
        test_first_message()
        
        # Test 2: Follow-up message
        test_follow_up_message()
        
        # Test 3: Multi-turn conversation
        test_multi_turn_conversation()
        
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
