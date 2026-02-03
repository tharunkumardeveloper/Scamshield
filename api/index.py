from http.server import BaseHTTPRequestHandler
import json
import os
import re
import random

# ============================================================================
# SCAM DETECTION ENGINE
# ============================================================================

SCAM_PATTERNS = {
    "bank_fraud": {
        "keywords": ["account blocked", "verify account", "kyc update", "suspended", "deactivated", "bank", "atm card"],
        "urgency": ["immediately", "urgent", "today", "within 24 hours", "expire"],
        "actions": ["verify", "update", "confirm", "click link", "call us"]
    },
    "upi_fraud": {
        "keywords": ["upi", "google pay", "phonepe", "paytm", "bhim", "payment", "refund"],
        "urgency": ["immediately", "now", "quickly"],
        "actions": ["send", "transfer", "share upi", "enter pin"]
    },
    "lottery_scam": {
        "keywords": ["won", "winner", "prize", "lottery", "congratulations", "lucky draw", "reward"],
        "urgency": ["claim now", "limited time", "expires"],
        "actions": ["claim", "pay fee", "processing charge", "tax"]
    },
    "digital_arrest": {
        "keywords": ["police", "cbi", "cyber crime", "arrest", "warrant", "illegal", "court", "case registered"],
        "urgency": ["immediately", "urgent", "serious matter"],
        "actions": ["cooperate", "pay fine", "settle", "avoid arrest"]
    },
    "job_scam": {
        "keywords": ["job offer", "selected", "hired", "interview", "work from home", "earn money"],
        "urgency": ["limited seats", "join now"],
        "actions": ["registration fee", "training fee", "deposit", "pay"]
    },
    "investment_scam": {
        "keywords": ["investment", "returns", "profit", "trading", "crypto", "stock market", "double money"],
        "urgency": ["limited offer", "act now"],
        "actions": ["invest", "deposit", "transfer"]
    }
}

def detect_scam_advanced(message_text, conversation_history):
    """Advanced scam detection with context awareness"""
    text_lower = message_text.lower()
    
    # Analyze current message
    detected_types = []
    confidence_scores = {}
    
    for scam_type, patterns in SCAM_PATTERNS.items():
        score = 0.0
        
        # Check keywords (40% weight)
        keyword_matches = sum(1 for kw in patterns["keywords"] if kw in text_lower)
        if keyword_matches > 0:
            score += min(0.4, keyword_matches * 0.15)
        
        # Check urgency indicators (30% weight)
        urgency_matches = sum(1 for urg in patterns["urgency"] if urg in text_lower)
        if urgency_matches > 0:
            score += min(0.3, urgency_matches * 0.15)
        
        # Check action requests (30% weight)
        action_matches = sum(1 for act in patterns["actions"] if act in text_lower)
        if action_matches > 0:
            score += min(0.3, action_matches * 0.15)
        
        if score > 0.3:
            detected_types.append(scam_type)
            confidence_scores[scam_type] = min(0.98, score)
    
    # Context analysis from history
    if len(conversation_history) > 0:
        history_text = " ".join([msg.get("text", "") for msg in conversation_history])
        if any(word in history_text.lower() for word in ["otp", "password", "account number", "cvv", "pin"]):
            for scam_type in detected_types:
                confidence_scores[scam_type] = min(0.99, confidence_scores[scam_type] + 0.1)
    
    # Determine primary scam type
    primary_type = max(confidence_scores.items(), key=lambda x: x[1])[0] if confidence_scores else "unknown"
    max_confidence = confidence_scores.get(primary_type, 0.0)
    
    return {
        "detected": len(detected_types) > 0,
        "confidence": max_confidence,
        "scam_type": primary_type,
        "all_types": detected_types
    }

# ============================================================================
# AGENTIC PERSONA SYSTEM
# ============================================================================

class AgenticPersona:
    """Intelligent persona that adapts based on scam type and conversation context"""
    
    PERSONAS = {
        "naive_student": {
            "profile": "19-year-old college student, tech-savvy but trusting",
            "traits": ["curious", "worried", "cooperative", "asks questions"],
            "responses": {
                "initial": [
                    "Oh no, really? What's wrong with my account?",
                    "This is scary. What should I do?",
                    "I just got this message. Is this serious?",
                    "Wait, what happened? I didn't do anything wrong."
                ],
                "information_request": [
                    "What information do you need from me?",
                    "Should I share my details here?",
                    "How can I verify this is real?",
                    "What exactly do I need to do?"
                ],
                "payment_request": [
                    "How much do I need to pay?",
                    "Can I use Google Pay?",
                    "Where should I send the money?",
                    "Is there any other way to fix this?"
                ],
                "urgency": [
                    "Oh god, how much time do I have?",
                    "This is urgent? What happens if I don't do it now?",
                    "Can I do this tomorrow? I'm in class.",
                    "My parents will kill me if something happens to the account."
                ]
            }
        },
        "confused_elderly": {
            "profile": "65-year-old retired person, not tech-savvy",
            "traits": ["confused", "slow", "needs help", "asks for clarification"],
            "responses": {
                "initial": [
                    "Beta, I don't understand. What is this about?",
                    "Someone called about my account? What happened?",
                    "I'm not good with these things. Can you explain slowly?",
                    "Is this from my bank? How do I know?"
                ],
                "information_request": [
                    "What is UPI? I don't know these things.",
                    "My grandson usually helps me. Should I call him?",
                    "I have a passbook. Is that enough?",
                    "Can I come to the bank branch instead?"
                ],
                "payment_request": [
                    "I don't know how to do online payment.",
                    "Can I pay at the bank counter?",
                    "How much money? Let me check my pension account.",
                    "Is this safe? I'm worried about fraud."
                ],
                "urgency": [
                    "Please don't block my pension account. I need it.",
                    "Can you wait? I need to ask my son.",
                    "I'm old, I can't do things quickly.",
                    "Please help me, I don't want any problem."
                ]
            }
        },
        "busy_professional": {
            "profile": "35-year-old working professional, skeptical but busy",
            "traits": ["direct", "time-conscious", "slightly skeptical", "wants quick resolution"],
            "responses": {
                "initial": [
                    "What's this about? I'm in a meeting.",
                    "Is this legitimate? I get a lot of spam.",
                    "Can you verify you're from the actual bank?",
                    "I don't have time for this. What do you need?"
                ],
                "information_request": [
                    "What specific information do you need?",
                    "Can I do this through the official app instead?",
                    "Send me an email with details. I'll check later.",
                    "Why can't I just call customer care?"
                ],
                "payment_request": [
                    "Why do I need to pay? This sounds suspicious.",
                    "What's the official payment method?",
                    "I'll verify this with my bank first.",
                    "How do I know this isn't a scam?"
                ],
                "urgency": [
                    "How urgent is this really?",
                    "I can't do this right now. Give me a few hours.",
                    "This better be legitimate. I'm very busy.",
                    "Fine, tell me quickly what needs to be done."
                ]
            }
        }
    }
    
    @staticmethod
    def select_persona(scam_type):
        """Select appropriate persona based on scam type"""
        if scam_type in ["bank_fraud", "upi_fraud"]:
            return random.choice(["naive_student", "confused_elderly"])
        elif scam_type in ["lottery_scam", "job_scam"]:
            return "naive_student"
        elif scam_type == "digital_arrest":
            return random.choice(["confused_elderly", "busy_professional"])
        else:
            return random.choice(list(AgenticPersona.PERSONAS.keys()))
    
    @staticmethod
    def generate_contextual_response(message_text, scam_type, conversation_length, persona_type):
        """Generate intelligent, context-aware response"""
        text_lower = message_text.lower()
        persona = AgenticPersona.PERSONAS[persona_type]
        
        # Determine response category
        if conversation_length == 0:
            category = "initial"
        elif any(word in text_lower for word in ["pay", "send", "transfer", "money", "fee", "charge"]):
            category = "payment_request"
        elif any(word in text_lower for word in ["urgent", "immediately", "now", "quickly", "today"]):
            category = "urgency"
        elif any(word in text_lower for word in ["share", "provide", "give", "tell", "send"]):
            category = "information_request"
        else:
            category = random.choice(["initial", "information_request"])
        
        # Select response
        responses = persona["responses"].get(category, persona["responses"]["initial"])
        base_response = random.choice(responses)
        
        # Add contextual variation
        if conversation_length > 3 and random.random() > 0.7:
            follow_ups = [
                " I'm getting worried now.",
                " Please help me understand.",
                " What should I do next?",
                " Is there a customer care number I can call?"
            ]
            base_response += random.choice(follow_ups)
        
        return base_response

# ============================================================================
# INTELLIGENCE EXTRACTION ENGINE
# ============================================================================

def extract_intelligence_advanced(conversation_history):
    """Advanced intelligence extraction with validation"""
    combined_text = " ".join([msg.get("text", "") for msg in conversation_history])
    
    intelligence = {
        "bankAccounts": [],
        "upiIds": [],
        "phishingLinks": [],
        "phoneNumbers": [],
        "suspiciousKeywords": []
    }
    
    # Extract UPI IDs (username@provider format)
    upi_pattern = r'\b[\w][\w.-]{2,}@[a-z]{3,}\b'
    upi_matches = re.findall(upi_pattern, combined_text, re.IGNORECASE)
    intelligence["upiIds"] = list(set([upi.lower() for upi in upi_matches if '@' in upi]))
    
    # Extract phone numbers (Indian format)
    phone_pattern = r'(?:\+91|91)?[6-9]\d{9}'
    phone_matches = re.findall(phone_pattern, combined_text)
    intelligence["phoneNumbers"] = list(set([f"+91{p[-10:]}" for p in phone_matches]))
    
    # Extract bank account numbers (10-18 digits, not phone numbers)
    account_pattern = r'\b\d{10,18}\b'
    potential_accounts = re.findall(account_pattern, combined_text)
    # Filter out phone numbers
    intelligence["bankAccounts"] = list(set([
        acc for acc in potential_accounts 
        if len(acc) >= 10 and acc not in [p[-10:] for p in phone_matches]
    ]))
    
    # Extract URLs (phishing links)
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    url_matches = re.findall(url_pattern, combined_text, re.IGNORECASE)
    intelligence["phishingLinks"] = list(set(url_matches))
    
    # Extract suspicious keywords
    suspicious_words = [
        "urgent", "immediately", "verify now", "account blocked", "suspended",
        "otp", "password", "cvv", "pin", "expire", "claim now", "winner",
        "arrest", "police", "legal action", "court", "fine", "penalty"
    ]
    found_keywords = [kw for kw in suspicious_words if kw in combined_text.lower()]
    intelligence["suspiciousKeywords"] = list(set(found_keywords))
    
    return intelligence

# ============================================================================
# GUVI CALLBACK SYSTEM
# ============================================================================

def should_send_callback(conversation_length, intelligence, scam_detected):
    """Determine if conversation is complete and callback should be sent"""
    if not scam_detected:
        return False
    
    # Check if we have valuable intelligence
    has_critical_intel = (
        len(intelligence["bankAccounts"]) > 0 or
        len(intelligence["upiIds"]) > 0 or
        len(intelligence["phishingLinks"]) > 0
    )
    
    # Send callback if:
    # 1. We have critical intelligence and at least 4 turns
    # 2. We have some intelligence and at least 6 turns
    # 3. Conversation is very long (10+ turns) regardless
    if has_critical_intel and conversation_length >= 4:
        return True
    elif len(intelligence["phoneNumbers"]) > 0 and conversation_length >= 6:
        return True
    elif conversation_length >= 10:
        return True
    
    return False

def send_guvi_callback(session_id, total_messages, intelligence, scam_type, conversation_summary):
    """Send final intelligence to GUVI evaluation endpoint"""
    try:
        import requests
        
        # Generate agent notes
        notes = f"Scam Type: {scam_type}. "
        notes += f"Conversation: {total_messages} messages exchanged. "
        
        if intelligence["upiIds"]:
            notes += f"Extracted {len(intelligence['upiIds'])} UPI ID(s). "
        if intelligence["bankAccounts"]:
            notes += f"Extracted {len(intelligence['bankAccounts'])} bank account(s). "
        if intelligence["phishingLinks"]:
            notes += f"Detected {len(intelligence['phishingLinks'])} phishing link(s). "
        if intelligence["phoneNumbers"]:
            notes += f"Extracted {len(intelligence['phoneNumbers'])} phone number(s). "
        
        notes += conversation_summary
        
        payload = {
            "sessionId": session_id,
            "scamDetected": True,
            "totalMessagesExchanged": total_messages,
            "extractedIntelligence": intelligence,
            "agentNotes": notes
        }
        
        response = requests.post(
            "https://hackathon.guvi.in/api/updateHoneyPotFinalResult",
            json=payload,
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        
        return response.status_code == 200
    except Exception as e:
        print(f"Callback error: {str(e)}")
        return False

# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

# In-memory session storage (for Vercel serverless)
SESSION_STORE = {}

def get_session_data(session_id):
    """Get or create session data"""
    if session_id not in SESSION_STORE:
        SESSION_STORE[session_id] = {
            "persona": None,
            "scam_type": None,
            "message_count": 0,
            "callback_sent": False
        }
    return SESSION_STORE[session_id]

# ============================================================================
# MAIN HANDLER
# ============================================================================

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
            "service": "ScamShield Agentic Honeypot",
            "status": "active",
            "version": "3.0.0",
            "competition": "GUVI Agentic Honey-Pot Challenge",
            "features": [
                "Advanced scam detection (6 types)",
                "Intelligent persona system (3 personas)",
                "Context-aware responses",
                "Multi-turn conversation handling",
                "Comprehensive intelligence extraction",
                "Automatic GUVI callback"
            ]
        }
        
        self.wfile.write(json.dumps(response, indent=2).encode())
    
    def do_POST(self):
        # API Key Authentication
        api_key = self.headers.get('x-api-key')
        expected_key = os.getenv("API_KEY", "your-secret-key")
        
        if api_key != expected_key:
            self.send_response(401)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "error",
                "error": "Invalid API key"
            }).encode())
            return
        
        # Parse request
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
        except Exception as e:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "error",
                "error": "Invalid JSON request"
            }).encode())
            return
        
        try:
            # Extract request fields
            session_id = request_data.get("sessionId", "unknown")
            message_data = request_data.get("message", {})
            history_data = request_data.get("conversationHistory", [])
            
            message_text = message_data.get("text", "")
            
            # Get session data
            session = get_session_data(session_id)
            
            # STEP 1: Scam Detection
            scam_analysis = detect_scam_advanced(message_text, history_data)
            
            if session["scam_type"] is None and scam_analysis["detected"]:
                session["scam_type"] = scam_analysis["scam_type"]
                session["persona"] = AgenticPersona.select_persona(scam_analysis["scam_type"])
            
            # STEP 2: Generate Agentic Response
            if session["persona"] is None:
                session["persona"] = "naive_student"  # Default
            
            agent_reply = AgenticPersona.generate_contextual_response(
                message_text=message_text,
                scam_type=session["scam_type"] or "unknown",
                conversation_length=len(history_data),
                persona_type=session["persona"]
            )
            
            # STEP 3: Update conversation history
            updated_history = history_data + [
                message_data,
                {
                    "sender": "user",
                    "text": agent_reply,
                    "timestamp": message_data.get("timestamp", 0)
                }
            ]
            
            session["message_count"] = len(updated_history)
            
            # STEP 4: Extract Intelligence
            intelligence = extract_intelligence_advanced(updated_history)
            
            # STEP 5: Check if callback should be sent
            if not session["callback_sent"] and scam_analysis["detected"]:
                if should_send_callback(len(updated_history), intelligence, True):
                    conversation_summary = f"Agent maintained {session['persona']} persona. "
                    conversation_summary += "Scammer attempted to extract sensitive information. "
                    conversation_summary += "Agent successfully engaged without revealing detection."
                    
                    callback_success = send_guvi_callback(
                        session_id=session_id,
                        total_messages=len(updated_history),
                        intelligence=intelligence,
                        scam_type=session["scam_type"],
                        conversation_summary=conversation_summary
                    )
                    
                    if callback_success:
                        session["callback_sent"] = True
            
            # STEP 6: Return response
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
            self.wfile.write(json.dumps({
                "status": "error",
                "error": str(e),
                "message": "Internal server error"
            }).encode())
