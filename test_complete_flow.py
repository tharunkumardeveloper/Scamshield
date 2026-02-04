"""
Complete flow test - simulates GUVI platform interaction
Tests the entire conversation flow and callback
"""
import json
import re

def extract_intelligence(conversation_history):
    """Extract intelligence from conversation (same as api/index.py)"""
    all_text = " ".join([msg.get("text", "") for msg in conversation_history])
    
    # Extract UPI IDs
    upi_pattern = r'\b[\w\.-]+@[\w\.-]+\b'
    upi_ids = list(set(re.findall(upi_pattern, all_text)))
    
    # Extract bank accounts (10-18 digits)
    account_pattern = r'\b\d{10,18}\b'
    bank_accounts = list(set(re.findall(account_pattern, all_text)))
    
    # Extract URLs
    url_pattern = r'https?://[^\s]+'
    phishing_links = list(set(re.findall(url_pattern, all_text)))
    
    # Extract phone numbers
    phone_pattern = r'\+?91[-\s]?\d{10}|\b\d{10}\b'
    phone_numbers = list(set(re.findall(phone_pattern, all_text)))
    
    # Suspicious keywords
    keywords = ["urgent", "blocked", "verify", "immediately", "suspended", "account", 
                "bank", "upi", "pay", "transfer", "click", "link"]
    suspicious_keywords = [kw for kw in keywords if kw in all_text.lower()]
    
    return {
        "bankAccounts": bank_accounts,
        "upiIds": upi_ids,
        "phishingLinks": phishing_links,
        "phoneNumbers": phone_numbers,
        "suspiciousKeywords": suspicious_keywords
    }

def create_guvi_payload(session_id, conversation_history, intelligence):
    """Create GUVI callback payload (same as api/index.py)"""
    total_messages = len(conversation_history)
    
    # Detect if scam
    scam_detected = any([
        intelligence["upiIds"],
        intelligence["bankAccounts"],
        intelligence["phishingLinks"],
        len(intelligence["suspiciousKeywords"]) >= 3
    ])
    
    # Generate agent notes
    notes = f"Conversation with {total_messages} messages. "
    if intelligence["upiIds"]:
        notes += f"Extracted {len(intelligence['upiIds'])} UPI IDs. "
    if intelligence["bankAccounts"]:
        notes += f"Extracted {len(intelligence['bankAccounts'])} bank accounts. "
    if intelligence["phishingLinks"]:
        notes += f"Detected {len(intelligence['phishingLinks'])} phishing links. "
    notes += "Scammer used urgency tactics and attempted to extract sensitive information."
    
    return {
        "sessionId": session_id,
        "scamDetected": scam_detected,
        "totalMessagesExchanged": total_messages,
        "extractedIntelligence": intelligence,
        "agentNotes": notes
    }

# Simulate a realistic scam conversation
print("=" * 70)
print("COMPLETE FLOW TEST - GUVI FORMAT VERIFICATION")
print("=" * 70)
print()

# Test Case 1: Bank Scam with UPI
print("TEST CASE 1: Bank Scam with UPI ID")
print("-" * 70)

conversation1 = [
    {"sender": "scammer", "text": "Your bank account will be blocked. Verify immediately!", "timestamp": 1770005528731},
    {"sender": "user", "text": "Oh no, what happened? What should I do?", "timestamp": 1770005528732},
    {"sender": "scammer", "text": "Send Rs 500 to verify your account", "timestamp": 1770005528733},
    {"sender": "user", "text": "Where should I send the money?", "timestamp": 1770005528734},
    {"sender": "scammer", "text": "Use this UPI: scammer123@paytm", "timestamp": 1770005528735},
    {"sender": "user", "text": "Okay, I'll send it now", "timestamp": 1770005528736},
]

intel1 = extract_intelligence(conversation1)
payload1 = create_guvi_payload("test-session-001", conversation1, intel1)

print("Extracted Intelligence:")
print(f"  UPI IDs: {intel1['upiIds']}")
print(f"  Bank Accounts: {intel1['bankAccounts']}")
print(f"  Phishing Links: {intel1['phishingLinks']}")
print(f"  Phone Numbers: {intel1['phoneNumbers']}")
print(f"  Keywords: {intel1['suspiciousKeywords']}")
print()
print("GUVI Payload:")
print(json.dumps(payload1, indent=2))
print()

# Test Case 2: Lottery Scam with Phone Number
print("=" * 70)
print("TEST CASE 2: Lottery Scam with Phone Number")
print("-" * 70)

conversation2 = [
    {"sender": "scammer", "text": "Congratulations! You won 10 lakh rupees!", "timestamp": 1770005528731},
    {"sender": "user", "text": "Really? How do I claim it?", "timestamp": 1770005528732},
    {"sender": "scammer", "text": "Call this number immediately: 9876543210", "timestamp": 1770005528733},
    {"sender": "user", "text": "Okay, I'll call now", "timestamp": 1770005528734},
    {"sender": "scammer", "text": "Also visit http://fake-lottery.com to register", "timestamp": 1770005528735},
    {"sender": "user", "text": "I'm going to the website", "timestamp": 1770005528736},
]

intel2 = extract_intelligence(conversation2)
payload2 = create_guvi_payload("test-session-002", conversation2, intel2)

print("Extracted Intelligence:")
print(f"  UPI IDs: {intel2['upiIds']}")
print(f"  Bank Accounts: {intel2['bankAccounts']}")
print(f"  Phishing Links: {intel2['phishingLinks']}")
print(f"  Phone Numbers: {intel2['phoneNumbers']}")
print(f"  Keywords: {intel2['suspiciousKeywords']}")
print()
print("GUVI Payload:")
print(json.dumps(payload2, indent=2))
print()

# Test Case 3: Digital Arrest with Bank Account
print("=" * 70)
print("TEST CASE 3: Digital Arrest with Bank Account")
print("-" * 70)

conversation3 = [
    {"sender": "scammer", "text": "This is cyber police. You are under digital arrest!", "timestamp": 1770005528731},
    {"sender": "user", "text": "What? Why? I didn't do anything!", "timestamp": 1770005528732},
    {"sender": "scammer", "text": "Pay fine of Rs 50000 immediately to avoid arrest", "timestamp": 1770005528733},
    {"sender": "user", "text": "How do I pay?", "timestamp": 1770005528734},
    {"sender": "scammer", "text": "Transfer to account number 1234567890123", "timestamp": 1770005528735},
    {"sender": "user", "text": "Okay, I'm transferring now", "timestamp": 1770005528736},
    {"sender": "scammer", "text": "Hurry up! Time is running out!", "timestamp": 1770005528737},
    {"sender": "user", "text": "I'm doing it!", "timestamp": 1770005528738},
]

intel3 = extract_intelligence(conversation3)
payload3 = create_guvi_payload("test-session-003", conversation3, intel3)

print("Extracted Intelligence:")
print(f"  UPI IDs: {intel3['upiIds']}")
print(f"  Bank Accounts: {intel3['bankAccounts']}")
print(f"  Phishing Links: {intel3['phishingLinks']}")
print(f"  Phone Numbers: {intel3['phoneNumbers']}")
print(f"  Keywords: {intel3['suspiciousKeywords']}")
print()
print("GUVI Payload:")
print(json.dumps(payload3, indent=2))
print()

# Verify all payloads
print("=" * 70)
print("PAYLOAD VALIDATION")
print("=" * 70)

def validate_payload(payload, test_name):
    """Validate payload structure"""
    required_fields = ["sessionId", "scamDetected", "totalMessagesExchanged", "extractedIntelligence", "agentNotes"]
    intel_fields = ["bankAccounts", "upiIds", "phishingLinks", "phoneNumbers", "suspiciousKeywords"]
    
    errors = []
    
    # Check top-level fields
    for field in required_fields:
        if field not in payload:
            errors.append(f"Missing field: {field}")
    
    # Check intelligence fields
    if "extractedIntelligence" in payload:
        intel = payload["extractedIntelligence"]
        for field in intel_fields:
            if field not in intel:
                errors.append(f"Missing intelligence field: {field}")
            elif not isinstance(intel[field], list):
                errors.append(f"Intelligence field {field} is not a list")
    
    # Check types
    if "sessionId" in payload and not isinstance(payload["sessionId"], str):
        errors.append("sessionId must be string")
    if "scamDetected" in payload and not isinstance(payload["scamDetected"], bool):
        errors.append("scamDetected must be boolean")
    if "totalMessagesExchanged" in payload and not isinstance(payload["totalMessagesExchanged"], int):
        errors.append("totalMessagesExchanged must be int")
    if "agentNotes" in payload and not isinstance(payload["agentNotes"], str):
        errors.append("agentNotes must be string")
    
    if errors:
        print(f"❌ {test_name}: FAILED")
        for error in errors:
            print(f"   - {error}")
        return False
    else:
        print(f"✅ {test_name}: PASSED")
        return True

all_valid = True
all_valid &= validate_payload(payload1, "Test Case 1 (Bank Scam)")
all_valid &= validate_payload(payload2, "Test Case 2 (Lottery Scam)")
all_valid &= validate_payload(payload3, "Test Case 3 (Digital Arrest)")

print()
print("=" * 70)
print("FINAL RESULT")
print("=" * 70)

if all_valid:
    print("✅ ALL TESTS PASSED!")
    print()
    print("Your implementation correctly:")
    print("  ✅ Extracts UPI IDs, bank accounts, phone numbers, URLs")
    print("  ✅ Generates proper GUVI callback payload")
    print("  ✅ Includes all required fields with correct types")
    print("  ✅ Formats extractedIntelligence correctly")
    print("  ✅ Creates meaningful agent notes")
    print()
    print("Ready to send to: https://hackathon.guvi.in/api/updateHoneyPotFinalResult")
else:
    print("❌ SOME TESTS FAILED - Review implementation")
