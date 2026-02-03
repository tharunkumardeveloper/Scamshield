import re

class IntelligenceExtractor:
    def __init__(self):
        self.patterns = {
            "upi_id": r'\b[\w.-]+@[\w.-]+\b',
            "phone": r'\b[6-9]\d{9}\b',
            "bank_account": r'\b\d{9,18}\b',
            "ifsc": r'\b[A-Z]{4}0[A-Z0-9]{6}\b',
            "url": r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        }
        
        self.scam_keywords = [
            "urgent", "verify now", "account blocked", "lottery", "prize", "won", 
            "blocked", "suspended", "verify", "arrest", "police", "CBI", 
            "payment", "fee", "charges", "OTP", "password", "immediately"
        ]
    
    def extract(self, conversation_history: list):
        """Extract intelligence from entire conversation history"""
        combined_text = " ".join([msg.text for msg in conversation_history])
        
        extracted = {
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "suspiciousKeywords": []
        }
        
        # Extract UPI IDs
        upi_matches = re.findall(self.patterns["upi_id"], combined_text)
        extracted["upiIds"] = list(set(upi_matches))
        
        # Extract phone numbers
        phone_matches = re.findall(self.patterns["phone"], combined_text)
        extracted["phoneNumbers"] = [f"+91{p}" for p in set(phone_matches)]
        
        # Extract bank accounts (filter out small numbers)
        account_matches = re.findall(self.patterns["bank_account"], combined_text)
        extracted["bankAccounts"] = [a for a in set(account_matches) if len(a) >= 10]
        
        # Extract URLs
        url_matches = re.findall(self.patterns["url"], combined_text)
        extracted["phishingLinks"] = list(set(url_matches))
        
        # Extract keywords
        message_lower = combined_text.lower()
        extracted["suspiciousKeywords"] = list(set([kw for kw in self.scam_keywords if kw in message_lower]))
        
        return extracted
