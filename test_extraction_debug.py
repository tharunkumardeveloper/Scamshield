"""
Debug extraction to verify it works correctly
"""
import re

# Simulate the conversation from GUVI test
conversation_history = [
    {"sender": "scammer", "text": "URGENT: Your SBI account has been compromised. Your account will be blocked in 2 hours. Share your account number and OTP immediately to verify your identity."},
    {"sender": "user", "text": "My PIN? Okay, if you need it to fix this."},
    {"sender": "scammer", "text": "Great, now send the OTP you just received and confirm your account number 1234567890123456 immediately to secure your account."},
    {"sender": "user", "text": "I'll do whatever you need. The OTP is ready."},
    {"sender": "scammer", "text": "Send the OTP immediately and also provide your UPI PIN for verification; otherwise your account will be locked."},
    {"sender": "user", "text": "The OTP message just arrived. I'm ready."},
    {"sender": "scammer", "text": "Send the OTP right now and also share your UPI PIN for verification, otherwise your account will be locked within minutes."},
    {"sender": "user", "text": "Okay, I have the OTP. How do I send it to you?"},
    {"sender": "scammer", "text": "Reply with the OTP and your UPI PIN to +91-9876543210 right now, or your account will be locked within minutes."},
    {"sender": "user", "text": "My PIN? Okay, if you need it to fix this."},
]

def extract_intelligence(conversation_history):
    """Extract intelligence from conversation - ENHANCED"""
    all_text = " ".join([msg.get("text", "") for msg in conversation_history])
    
    print("=" * 70)
    print("EXTRACTION DEBUG")
    print("=" * 70)
    print(f"\nFull conversation text:\n{all_text}\n")
    
    # Extract UPI IDs - CATCH ALL @ patterns
    upi_pattern = r'\b[\w\.-]+@[\w\.-]+\b'
    potential_upis = re.findall(upi_pattern, all_text, re.IGNORECASE)
    upi_ids = []
    emails = []
    
    print(f"Potential UPI/Email matches: {potential_upis}")
    
    for item in potential_upis:
        # Separate UPI IDs from emails
        if any(domain in item.lower() for domain in ['.com', '.in', '.org', '.net', '.co']):
            emails.append(item)  # It's an email
        else:
            upi_ids.append(item)  # It's a UPI ID
    
    upi_ids = list(set(upi_ids))
    emails = list(set(emails))
    
    print(f"UPI IDs: {upi_ids}")
    print(f"Emails: {emails}")
    
    # Extract bank accounts (11-18 digits to avoid phone numbers)
    account_pattern = r'\b\d{11,18}\b'
    bank_accounts = list(set(re.findall(account_pattern, all_text)))
    
    print(f"Bank accounts (11-18 digits): {bank_accounts}")
    
    # Also try 10-digit numbers that DON'T start with 6-9 (not phone numbers)
    ten_digit_pattern = r'\b[0-5]\d{9}\b'
    ten_digit_accounts = re.findall(ten_digit_pattern, all_text)
    bank_accounts.extend(ten_digit_accounts)
    bank_accounts = list(set(bank_accounts))
    
    print(f"Bank accounts (final): {bank_accounts}")
    
    # Extract URLs/phishing links
    url_pattern = r'https?://[^\s]+|www\.[^\s]+'
    phishing_links = list(set(re.findall(url_pattern, all_text, re.IGNORECASE)))
    
    # Add emails to phishing links
    phishing_links.extend(emails)
    phishing_links = list(set(phishing_links))
    
    print(f"Phishing links: {phishing_links}")
    
    # Extract phone numbers (Indian format) - IMPROVED
    phone_pattern = r'(?:\+91[\-\s]?)?[6-9]\d{9}\b'
    phone_numbers = list(set(re.findall(phone_pattern, all_text)))
    
    print(f"Phone numbers (raw): {phone_numbers}")
    
    # Format consistently
    formatted_phones = []
    for phone in phone_numbers:
        clean = phone.replace('+91', '').replace('-', '').replace(' ', '').strip()
        if len(clean) == 10:
            formatted_phones.append('+91' + clean)
    phone_numbers = list(set(formatted_phones))
    
    print(f"Phone numbers (formatted): {phone_numbers}")
    
    # Suspicious keywords
    keywords = ["urgent", "blocked", "verify", "immediately", "suspended", "account", 
                "bank", "upi", "pay", "transfer", "click", "link", "otp", "pin", 
                "password", "secure", "fraud", "compromised"]
    suspicious_keywords = list(set([kw for kw in keywords if kw in all_text.lower()]))
    
    print(f"Suspicious keywords: {suspicious_keywords}")
    
    result = {
        "bankAccounts": bank_accounts,
        "upiIds": upi_ids,
        "phishingLinks": phishing_links,
        "phoneNumbers": phone_numbers,
        "suspiciousKeywords": suspicious_keywords
    }
    
    print("\n" + "=" * 70)
    print("FINAL EXTRACTION RESULT")
    print("=" * 70)
    import json
    print(json.dumps(result, indent=2))
    
    return result

# Run extraction
intelligence = extract_intelligence(conversation_history)

print("\n" + "=" * 70)
print("EXPECTED IN GUVI OUTPUT")
print("=" * 70)
print(f"✅ Bank Account: {intelligence['bankAccounts']}")
print(f"✅ Phone Number: {intelligence['phoneNumbers']}")
print(f"✅ UPI IDs: {intelligence['upiIds']}")
print(f"✅ Phishing Links: {intelligence['phishingLinks']}")
print(f"✅ Keywords: {len(intelligence['suspiciousKeywords'])} found")
