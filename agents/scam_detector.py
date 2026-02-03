class ScamDetector:
    def __init__(self):
        self.scam_keywords = {
            "lottery_scam": ["won", "prize", "lottery", "congratulations", "claim"],
            "bank_scam": ["account blocked", "verify", "KYC", "suspended", "update"],
            "digital_arrest": ["police", "CBI", "arrest", "illegal", "case"],
            "investment_scam": ["returns", "profit", "investment", "double money"],
            "job_scam": ["hired", "selected", "registration fee", "training fee"]
        }
    
    def analyze(self, message: str, history: list):
        message_lower = message.lower()
        
        # Detect scam type
        detected_types = []
        for scam_type, keywords in self.scam_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_types.append(scam_type)
        
        # Calculate confidence
        confidence = 0.0
        if detected_types:
            confidence = min(0.95, 0.6 + (len(detected_types) * 0.1))
        
        return {
            "detected": len(detected_types) > 0,
            "confidence": confidence,
            "scam_type": detected_types[0] if detected_types else "unknown"
        }
