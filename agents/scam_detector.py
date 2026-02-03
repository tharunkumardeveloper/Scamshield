class ScamDetector:
    def __init__(self):
        self.scam_keywords = {
            "bank_scam": ["account blocked", "verify", "KYC", "suspended", "update", "bank", "OTP", "password"],
            "lottery_scam": ["won", "prize", "lottery", "congratulations", "claim", "winner"],
            "digital_arrest": ["police", "CBI", "arrest", "illegal", "case", "court", "warrant"],
            "investment_scam": ["returns", "profit", "investment", "double money", "trading"],
            "job_scam": ["hired", "selected", "registration fee", "training fee", "job offer"],
            "upi_scam": ["UPI", "Google Pay", "PhonePe", "Paytm", "send money", "transfer"]
        }
    
    def analyze(self, message_text: str, history: list):
        """Analyze message for scam intent"""
        message_lower = message_text.lower()
        
        # Detect scam type
        detected_types = []
        for scam_type, keywords in self.scam_keywords.items():
            if any(keyword.lower() in message_lower for keyword in keywords):
                detected_types.append(scam_type)
        
        # Calculate confidence
        confidence = 0.0
        if detected_types:
            confidence = min(0.95, 0.6 + (len(detected_types) * 0.1))
        
        # Check for urgency indicators (increases scam likelihood)
        urgency_words = ["urgent", "immediately", "now", "quickly", "hurry", "today", "hours"]
        if any(word in message_lower for word in urgency_words):
            confidence = min(0.98, confidence + 0.15)
        
        return {
            "detected": len(detected_types) > 0 or confidence > 0.5,
            "confidence": confidence,
            "scam_type": detected_types[0] if detected_types else "unknown",
            "all_types": detected_types
        }
