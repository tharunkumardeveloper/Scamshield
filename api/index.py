from http.server import BaseHTTPRequestHandler
import json
import os
import re
import random

# Scam detection keywords
SCAM_KEYWORDS = {
    "bank_scam": ["account blocked", "verify", "kyc", "suspended", "update", "bank", "otp", "password"],
    "lottery_scam": ["won", "prize", "lottery", "congratulations", "claim", "winner"],
    "digital_arrest": ["police", "cbi", "arrest", "illegal", "case", "court", "warrant"],
    "investment_scam": ["returns", "profit", "investment", "double money", "trading"],
    "job_scam": ["hired", "selected", "registration fee", "training fee", "job offer"],
    "upi_scam": ["upi", "google pay", "phonepe", "paytm", "send money", "transfer"]
}

URGENCY_WORDS = ["urgent", "immediately", "now", "quickly", "hurry", "today", "hours"]

# Persona responses
PERSONA_RESPONSES = {
    "concerned": [
        "Oh no, what happened? What should I do?",
        "This sounds serious. Can you help me?",
        "I'm worried. Please tell me what to do.",
        "What do I need to do to fix this?"
    ],
    "confused": [
        "I don't understand. Can you explain?",
        "What does this mean? I'm not sure what to do.",
        "Can you tell me more details?",
        "I'm confused. Please explain slowly."
    ],
    "cooperative": [
        "Okay, I want to help. What information do you need?",
        "I'll do whatever is needed. Just tell me.",
        "Yes, I can do that. What's next?",
        "I'm ready. Please guide me."
    ]
}

def detect_scam(message_text):
    """Detect if message is a scam"""
    message_lower = message_text.lower()
    
    detected_types = []
    for scam_type, keywords in SCAM_KEYWORDS.items():
        if any(keyword.lower() in message_lower for keyword in keywords):
            detected_types.append(scam_type)
    
    confidence = 0.0
    if detected_types:
        confidence = min(0.95, 0.6 + (len(detected_types) * 0.1))
    
    if any(word in message_lower for word in URGENCY_WORDS):
        confidence = min(0.98, confidence + 0.15)
    
    return {
        "detected": len(detected_types) > 0 or confidence > 0.5,
        "confidence": confidence,
        "scam_type": detected_types[0] if detected_types else "unknown"
    }

def generate_response(message_text, history_length):
    """Generate a simple response"""
    message_lower = message_text.lower()
    
    # Choose response type based on message content
    if any(word in message_lower for word in ["account", "blocked", "suspended"]):
        responses = PERSONA_RESPONSES["concerned"]
    elif any(word in message_lower for word in ["upi", "pay", "send", "transfer"]):
        responses = PERSONA_RESPONSES["cooperative"]
    else:
        responses = PERSONA_RESPONSES["confused"]
    
    return random.choice(responses)

def extract_intelligence(conversation_history):
    """Extract intelligence from conversation"""
    combined_text = " ".join([msg.get("text", "") for msg in conversation_history])
    
    # Extract UPI IDs
    upi_pattern = r'\b[\w.-]+@[\w.-]+\b'
    upi_ids = list(set(re.findall(upi_pattern, combined_text)))
    
    # Extract phone numbers
    phone_pattern = r'\b[6-9]\d{9}\b'
    phone_matches = re.findall(phone_pattern, combined_text)
    phone_numbers = [f"+91{p}" for p in set(phone_matches)]
    
    # Extract bank accounts
    account_pattern = r'\b\d{9,18}\b'
    account_matches = re.findall(account_pattern, combined_text)
    bank_accounts = [a for a in set(account_matches) if len(a) >= 10]
    
    # Extract URLs
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    phishing_links = list(set(re.findall(url_pattern, combined_text)))
    
    # Extract keywords
    keywords = []
    for word in ["urgent", "verify now", "account blocked", "otp", "password", "immediately"]:
        if word in combined_text.lower():
            keywords.append(word)
    
    return {
        "bankAccounts": bank_accounts,
        "upiIds": upi_ids,
        "phishingLinks": phishing_links,
        "phoneNumbers": phone_numbers,
        "suspiciousKeywords": list(set(keywords))
    }

def send_guvi_callback(session_id, total_messages, intelligence, scam_type):
    """Send final result to GUVI"""
    import requests
    
    agent_notes = f"Scam type: {scam_type}. Engagement: {total_messages} messages. "
    if intelligence["upiIds"]:
        agent_notes += "Extracted UPI IDs. "
    if intelligence["bankAccounts"]:
        agent_notes += "Extracted bank accounts. "
    if intelligence["phishingLinks"]:
        agent_notes += "Detected phishing links. "
    agent_notes += "Intelligence extracted successfully."
    
    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": total_messages,
        "extractedIntelligence": intelligence,
        "agentNotes": agent_notes
    }
    
    try:
        response = requests.post(
            "https://hackathon.guvi.in/api/updateHoneyPotFinalResult",
            json=payload,
            timeout=5,
            headers={"Content-Type": "application/json"}
        )
        return response.status_code == 200
    except:
        return False

class handler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, x-api-key')
        self.end_headers()
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "service": "ScamShield Honeypot API",
            "status": "active",
            "version": "2.0.0",
            "competition": "GUVI Agentic Honey-Pot Challenge",
            "endpoint": "POST /api/honeypot"
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        # Verify API key
        api_key = self.headers.get('x-api-key')
        expected_key = os.getenv("API_KEY", "your-secret-key")
        
        if api_key != expected_key:
            self.send_response(401)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid API key"}).encode())
            return
        
        # Read request body
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
        except Exception as e:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid request", "details": str(e)}).encode())
            return
        
        try:
            # Parse request
            session_id = request_data.get("sessionId", "unknown")
            message_data = request_data.get("message", {})
            history_data = request_data.get("conversationHistory", [])
            
            message_text = message_data.get("text", "")
            
            # Step 1: Detect scam
            scam_analysis = detect_scam(message_text)
            
            # Step 2: Generate response
            agent_reply = generate_response(message_text, len(history_data))
            
            # Step 3: Build updated history
            updated_history = history_data + [
                message_data,
                {"sender": "user", "text": agent_reply, "timestamp": message_data.get("timestamp", 0)}
            ]
            
            # Step 4: Extract intelligence
            intelligence = extract_intelligence(updated_history)
            
            # Step 5: Check if should send callback
            has_intelligence = (
                len(intelligence["bankAccounts"]) > 0 or
                len(intelligence["upiIds"]) > 0 or
                len(intelligence["phishingLinks"]) > 0 or
                len(intelligence["phoneNumbers"]) > 0
            )
            
            should_send_callback = (
                scam_analysis["detected"] and
                ((has_intelligence and len(updated_history) >= 5) or len(updated_history) >= 10)
            )
            
            if should_send_callback:
                send_guvi_callback(
                    session_id=session_id,
                    total_messages=len(updated_history),
                    intelligence=intelligence,
                    scam_type=scam_analysis["scam_type"]
                )
            
            # Return response
            response = {
                "status": "success",
                "reply": agent_reply
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = {
                "status": "error",
                "error": str(e),
                "message": "Internal server error"
            }
            self.wfile.write(json.dumps(error_response).encode())
