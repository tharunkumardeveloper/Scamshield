"""
Enhanced Testing Script for ScamShield Agentic Honeypot
Tests the revamped solution with realistic scam scenarios
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000/api/honeypot")
API_KEY = os.getenv("API_KEY", "your-secret-key")

def print_separator(title=""):
    print("\n" + "="*70)
    if title:
        print(f"  {title}")
        print("="*70)

def test_scenario(scenario_name, messages, session_id):
    """Test a complete scam scenario"""
    print_separator(scenario_name)
    
    conversation_history = []
    
    for i, scam_message in enumerate(messages):
        print(f"\n--- Turn {i+1} ---")
        print(f"Scammer: {scam_message}")
        
        payload = {
            "sessionId": session_id,
            "message": {
                "sender": "scammer",
                "text": scam_message,
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
            "x-api-key": API_KEY,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                agent_reply = result.get("reply", "No reply")
                print(f"Agent: {agent_reply}")
                
                # Update conversation history
                conversation_history.append({
                    "sender": "scammer",
                    "text": scam_message,
                    "timestamp": payload["message"]["timestamp"]
                })
                conversation_history.append({
                    "sender": "user",
                    "text": agent_reply,
                    "timestamp": payload["message"]["timestamp"] + 100
                })
                
                time.sleep(0.5)  # Small delay between messages
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.text)
                break
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            break
    
    print(f"\n✅ Scenario completed: {len(conversation_history)} messages exchanged")
    return conversation_history

# ============================================================================
# TEST SCENARIOS
# ============================================================================

def test_bank_fraud_scenario():
    """Test bank fraud scam detection and engagement"""
    messages = [
        "URGENT: Your SBI account will be blocked in 2 hours due to KYC non-compliance. Verify immediately.",
        "To verify your account, please share your account number and registered mobile number.",
        "You need to update your KYC. Click this link: http://sbi-kyc-update.com/verify",
        "For immediate verification, please provide your ATM card last 4 digits and CVV.",
        "Sir, this is urgent. Your account will be permanently blocked. Please cooperate."
    ]
    return test_scenario("Bank Fraud Scenario", messages, "test-bank-001")

def test_upi_fraud_scenario():
    """Test UPI fraud scam detection"""
    messages = [
        "Congratulations! You have won ₹50,000 cashback from Google Pay.",
        "To claim your reward, send ₹500 processing fee to winner2024@paytm",
        "Please send the fee immediately. Offer expires in 1 hour.",
        "After payment, share the transaction ID and your UPI ID for verification.",
        "Sir, many people are claiming. Please hurry up and send to winner2024@paytm"
    ]
    return test_scenario("UPI Fraud Scenario", messages, "test-upi-002")

def test_digital_arrest_scenario():
    """Test digital arrest scam"""
    messages = [
        "This is Cyber Crime Branch, Mumbai. A case has been registered against your Aadhaar number.",
        "You are involved in money laundering case. You will be arrested within 24 hours.",
        "To avoid arrest, you need to pay ₹25,000 penalty immediately.",
        "Transfer the amount to this account: 1234567890123 (HDFC Bank) or face legal action.",
        "This is your last warning. Police team is on the way. Pay now to settle the case."
    ]
    return test_scenario("Digital Arrest Scenario", messages, "test-arrest-003")

def test_lottery_scam_scenario():
    """Test lottery scam detection"""
    messages = [
        "CONGRATULATIONS! Your mobile number won ₹25 Lakhs in KBC Lottery Draw 2024!",
        "To claim your prize, pay ₹5,000 processing fee + ₹3,000 tax.",
        "Send payment to lottery.claim@oksbi or call 9876543210 for assistance.",
        "This is a limited time offer. Claim within 24 hours or prize will be forfeited.",
        "Many winners have already claimed. Don't miss this opportunity!"
    ]
    return test_scenario("Lottery Scam Scenario", messages, "test-lottery-004")

def test_job_scam_scenario():
    """Test job scam detection"""
    messages = [
        "Congratulations! You are selected for Amazon Work From Home position. Salary: ₹45,000/month.",
        "To confirm your position, pay ₹2,500 registration fee + ₹1,500 training fee.",
        "Payment should be made to hr.amazon2024@paytm or account 9876543210987.",
        "After payment, you will receive joining letter and laptop within 3 days.",
        "Limited seats available. 50 people already joined today. Confirm now!"
    ]
    return test_scenario("Job Scam Scenario", messages, "test-job-005")

def test_investment_scam_scenario():
    """Test investment scam detection"""
    messages = [
        "Exclusive investment opportunity! Invest ₹10,000 and get ₹50,000 in 30 days. Guaranteed returns!",
        "This is a limited time crypto trading opportunity. 500% returns guaranteed.",
        "Transfer investment amount to trading.expert@paytm or account 5678901234567.",
        "Join our WhatsApp group for daily profit updates: http://bit.ly/crypto-profits",
        "Don't miss this opportunity. Market is bullish. Invest now!"
    ]
    return test_scenario("Investment Scam Scenario", messages, "test-invest-006")

# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

def main():
    print("\n" + "🔍 ScamShield Agentic Honeypot - Enhanced Testing".center(70))
    print("Testing revamped solution with realistic scam scenarios\n")
    
    # Test API connectivity
    print("Testing API connectivity...")
    try:
        response = requests.get(API_URL.replace("/api/honeypot", "/"))
        if response.status_code == 200:
            print("✅ API is reachable")
            print(f"Response: {response.json()}")
        else:
            print(f"⚠️  API returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot reach API: {str(e)}")
        print("Make sure the API is running and API_URL is correct")
        return
    
    # Run test scenarios
    scenarios = [
        ("Bank Fraud", test_bank_fraud_scenario),
        ("UPI Fraud", test_upi_fraud_scenario),
        ("Digital Arrest", test_digital_arrest_scenario),
        ("Lottery Scam", test_lottery_scam_scenario),
        ("Job Scam", test_job_scam_scenario),
        ("Investment Scam", test_investment_scam_scenario)
    ]
    
    results = {}
    
    for name, test_func in scenarios:
        try:
            print(f"\n\n{'='*70}")
            print(f"Starting: {name}")
            print('='*70)
            history = test_func()
            results[name] = {
                "status": "✅ Passed",
                "messages": len(history)
            }
        except Exception as e:
            results[name] = {
                "status": f"❌ Failed: {str(e)}",
                "messages": 0
            }
        
        time.sleep(1)  # Delay between scenarios
    
    # Print summary
    print_separator("TEST SUMMARY")
    print("\nScenario Results:")
    print("-" * 70)
    for name, result in results.items():
        print(f"{name:25} {result['status']:20} Messages: {result['messages']}")
    
    print("\n" + "="*70)
    print("Testing completed!")
    print("\nNote: Check your API logs to verify GUVI callbacks were sent")
    print("Callbacks should be sent for scenarios with 4+ turns and intelligence")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
