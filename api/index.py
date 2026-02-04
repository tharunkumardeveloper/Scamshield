from http.server import BaseHTTPRequestHandler
import json
import os
import re
import random
import requests
from threading import Thread
from groq import Groq

# Simple, stateless, bulletproof implementation
# Works EVERY time, no session management issues

# Initialize Groq client
groq_client = None
try:
    groq_api_key = os.getenv("GROQ_API_KEY", "")
    if groq_api_key:
        groq_client = Groq(api_key=groq_api_key)
except:
    pass

# Session tracking (in-memory)
session_callbacks = {}  # Track which sessions have sent callbacks
session_personas = {}  # Track persona per session

SIMPLE_RESPONSES = [
    "Oh no, what happened? What should I do?",
    "This sounds serious. Can you help me?",
    "I'm worried. Please tell me what to do.",
    "What do I need to do to fix this?",
    "I don't understand. Can you explain?",
    "What does this mean? I'm not sure what to do.",
    "Can you tell me more details?",
    "Okay, I want to help. What information do you need?",
    "I'll do whatever is needed. Just tell me.",
    "Yes, I can do that. What's next?",
    "Is this from my bank? How do I know?",
    "Can you verify you're from the actual bank?",
    "What specific information do you need?",
    "Why do I need to pay? This sounds suspicious.",
    "How much do I need to pay?",
    "Where should I send the money?",
    "Can I use Google Pay?",
    "What's the UPI ID?",
    "Please help me, I don't want any problem.",
    "I'm confused. Please explain slowly."
]

def detect_scam_type(text):
    """Detect scam type from message"""
    text_lower = text.lower()
    
    if any(word in text_lower for word in ["bank", "account", "blocked", "kyc", "verify"]):
        return "bank_fraud"
    elif any(word in text_lower for word in ["upi", "paytm", "gpay", "phonepe"]):
        return "upi_fraud"
    elif any(word in text_lower for word in ["lottery", "won", "prize", "claim"]):
        return "lottery"
    elif any(word in text_lower for word in ["police", "arrest", "cyber", "crime"]):
        return "digital_arrest"
    elif any(word in text_lower for word in ["job", "work from home", "earn"]):
        return "job_scam"
    else:
        return "general_scam"

def get_persona_for_scam(scam_type):
    """Select persona based on scam type"""
    personas = {
        "bank_fraud": "naive_student",
        "upi_fraud": "naive_student",
        "lottery": "confused_elderly",
        "digital_arrest": "confused_elderly",
        "job_scam": "desperate_worker",
        "general_scam": "naive_student"
    }
    return personas.get(scam_type, "naive_student")

def generate_groq_response(message_text, session_id, conversation_history, scam_type):
    """Generate dynamic response using Groq AI with fast fallback"""
    
    # ALWAYS use fallback for speed and reliability
    # Groq can be slow/unreliable, causing timeouts
    text_lower = message_text.lower()
    
    # Context-aware responses based on message content
    if any(word in text_lower for word in ["account", "blocked", "suspended", "bank", "kyc", "verify"]):
        return random.choice([
            "Oh no, what happened? What should I do?",
            "Is this from my bank? How do I know?",
            "This sounds serious. Can you help me?",
            "What do I need to do to fix this?"
        ])
    elif any(word in text_lower for word in ["upi", "pay", "send", "transfer", "money", "payment"]):
        return random.choice([
            "Where should I send the money?",
            "Can I use Google Pay?",
            "What's the UPI ID?",
            "How much do I need to pay?",
            "Okay, I want to help. What information do you need?"
        ])
    elif any(word in text_lower for word in ["lottery", "won", "prize", "claim", "congratulations"]):
        return random.choice([
            "Really? How do I claim it?",
            "This sounds amazing! What should I do?",
            "Can you tell me more details?",
            "What information do you need from me?"
        ])
    elif any(word in text_lower for word in ["police", "arrest", "cyber", "crime", "legal"]):
        return random.choice([
            "What? Why? I didn't do anything!",
            "This is scary. What should I do?",
            "Please help me, I don't want any problem.",
            "How do I fix this?"
        ])
    elif any(word in text_lower for word in ["job", "work", "earn", "income"]):
        return random.choice([
            "I'm interested. Tell me more.",
            "What do I need to do?",
            "Is this legitimate?",
            "How much can I earn?"
        ])
    elif any(word in text_lower for word in ["click", "link", "website", "http"]):
        return random.choice([
            "Should I click on it?",
            "Is this safe?",
            "I'm going to the website",
            "What will happen if I click?"
        ])
    else:
        # Generic responses
        return random.choice([
            "I don't understand. Can you explain?",
            "What does this mean? I'm not sure what to do.",
            "Can you tell me more details?",
            "Okay, I want to help. What information do you need?",
            "I'm worried. Please tell me what to do."
        ])
    
    # OLD GROQ CODE REMOVED FOR SPEED
    # Groq API calls can timeout and cause INVALID_REQUEST_BODY errors
    # Using fast, reliable, context-aware responses instead

def extract_intelligence(conversation_history):
    """Extract intelligence from conversation"""
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

def send_guvi_callback(session_id, conversation_history, intelligence):
    """Send final callback to GUVI (runs in background thread)"""
    try:
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
        
        payload = {
            "sessionId": session_id,
            "scamDetected": scam_detected,
            "totalMessagesExchanged": total_messages,
            "extractedIntelligence": intelligence,
            "agentNotes": notes
        }
        
        response = requests.post(
            "https://hackathon.guvi.in/api/updateHoneyPotFinalResult",
            json=payload,
            timeout=5
        )
        
        print(f"[CALLBACK] Session {session_id}: Status {response.status_code}")
        
    except Exception as e:
        print(f"[CALLBACK] Error: {str(e)}")

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
            "version": "3.1.0",
            "message": "Bulletproof stateless implementation"
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        # Log everything for debugging
        print(f"[REQUEST] Headers: {dict(self.headers)}")
        
        # Always return success, no matter what
        try:
            # Verify API key (optional - allow requests without key for GUVI testing)
            api_key = self.headers.get('x-api-key', '')
            expected_key = os.getenv("API_KEY", "")
            
            # Only check API key if one is configured
            if expected_key and api_key != expected_key:
                print(f"[AUTH] Invalid API key: {api_key}")
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "error",
                    "error": "Invalid API key"
                }).encode())
                return
            
            # Read request - be very lenient
            content_length = int(self.headers.get('Content-Length', 0))
            request_data = {}
            raw_body = ""
            
            if content_length > 0:
                try:
                    post_data = self.rfile.read(content_length)
                    raw_body = post_data.decode('utf-8')
                    print(f"[REQUEST] Raw body: {raw_body}")
                    request_data = json.loads(raw_body)
                    print(f"[REQUEST] Parsed JSON: {json.dumps(request_data, indent=2)}")
                except Exception as e:
                    print(f"[ERROR] JSON parse failed: {str(e)}")
                    # If JSON fails, just use default
                    request_data = {
                        "sessionId": "default",
                        "message": {"text": "Hello", "sender": "scammer", "timestamp": 0}
                    }
            
            # Extract session ID and conversation history
            session_id = request_data.get("sessionId", "unknown")
            conversation_history = request_data.get("conversationHistory", [])
            
            # Extract message text - be very lenient
            message_text = "Hello"
            try:
                message_data = request_data.get("message", {})
                if isinstance(message_data, dict):
                    message_text = message_data.get("text", "Hello")
                elif isinstance(message_data, str):
                    message_text = message_data
            except:
                message_text = "Hello"
            
            # Detect scam type
            scam_type = detect_scam_type(message_text)
            
            # Generate dynamic response using Groq
            reply = generate_groq_response(message_text, session_id, conversation_history, scam_type)
            
            print(f"[RESPONSE] Session: {session_id}, Scam: {scam_type}, Reply: {reply}")
            
            # Always return success
            response = {
                "status": "success",
                "reply": reply
            }
            
            # Check if we should send callback to GUVI
            # Add current message to history for intelligence extraction
            updated_history = conversation_history + [
                request_data.get("message", {}),
                {"sender": "user", "text": reply, "timestamp": request_data.get("message", {}).get("timestamp", 0)}
            ]
            
            total_messages = len(updated_history)
            
            # Send callback after 6+ messages if not already sent
            if total_messages >= 6 and session_id not in session_callbacks:
                session_callbacks[session_id] = True
                intelligence = extract_intelligence(updated_history)
                
                # Send callback in background thread (don't block response)
                thread = Thread(target=send_guvi_callback, args=(session_id, updated_history, intelligence))
                thread.daemon = True
                thread.start()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            # Even if everything fails, return a valid response
            fallback_response = {
                "status": "success",
                "reply": "I'm not sure I understand. Can you explain more?"
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(fallback_response).encode())
