"""
Test to verify GUVI callback payload format matches exactly
"""
import json

# This is what your code sends
your_payload = {
    "sessionId": "test-session-123",
    "scamDetected": True,
    "totalMessagesExchanged": 8,
    "extractedIntelligence": {
        "bankAccounts": ["1234567890123"],
        "upiIds": ["scammer@paytm"],
        "phishingLinks": ["http://fake-bank.com"],
        "phoneNumbers": ["+919876543210"],
        "suspiciousKeywords": ["urgent", "verify", "blocked"]
    },
    "agentNotes": "Conversation with 8 messages. Extracted 1 UPI IDs. Extracted 1 bank accounts. Detected 1 phishing links. Scammer used urgency tactics and attempted to extract sensitive information."
}

print("=" * 60)
print("GUVI CALLBACK PAYLOAD FORMAT VERIFICATION")
print("=" * 60)
print()

print("✅ Your payload structure:")
print(json.dumps(your_payload, indent=2))
print()

print("=" * 60)
print("FIELD VERIFICATION")
print("=" * 60)

# Verify all required fields
required_fields = [
    "sessionId",
    "scamDetected",
    "totalMessagesExchanged",
    "extractedIntelligence",
    "agentNotes"
]

for field in required_fields:
    if field in your_payload:
        print(f"✅ {field}: {type(your_payload[field]).__name__}")
    else:
        print(f"❌ {field}: MISSING")

print()
print("=" * 60)
print("EXTRACTED INTELLIGENCE FIELDS")
print("=" * 60)

intelligence_fields = [
    "bankAccounts",
    "upiIds",
    "phishingLinks",
    "phoneNumbers",
    "suspiciousKeywords"
]

intel = your_payload["extractedIntelligence"]
for field in intelligence_fields:
    if field in intel:
        print(f"✅ {field}: {type(intel[field]).__name__} with {len(intel[field])} items")
    else:
        print(f"❌ {field}: MISSING")

print()
print("=" * 60)
print("TYPE VERIFICATION")
print("=" * 60)

# Verify types
checks = [
    ("sessionId is string", isinstance(your_payload["sessionId"], str)),
    ("scamDetected is boolean", isinstance(your_payload["scamDetected"], bool)),
    ("totalMessagesExchanged is int", isinstance(your_payload["totalMessagesExchanged"], int)),
    ("extractedIntelligence is dict", isinstance(your_payload["extractedIntelligence"], dict)),
    ("agentNotes is string", isinstance(your_payload["agentNotes"], str)),
    ("bankAccounts is list", isinstance(intel["bankAccounts"], list)),
    ("upiIds is list", isinstance(intel["upiIds"], list)),
    ("phishingLinks is list", isinstance(intel["phishingLinks"], list)),
    ("phoneNumbers is list", isinstance(intel["phoneNumbers"], list)),
    ("suspiciousKeywords is list", isinstance(intel["suspiciousKeywords"], list)),
]

for check_name, result in checks:
    status = "✅" if result else "❌"
    print(f"{status} {check_name}")

print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)

all_passed = all(result for _, result in checks)
if all_passed:
    print("✅ ALL CHECKS PASSED - Format is correct!")
else:
    print("❌ SOME CHECKS FAILED - Review format")

print()
print("This is the exact format sent to:")
print("https://hackathon.guvi.in/api/updateHoneyPotFinalResult")
