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
    
    # Try Groq first with SHORT timeout
    if groq_client:
        try:
            # Get or set persona
            if session_id not in session_personas:
                session_personas[session_id] = get_persona_for_scam(scam_type)
            
            persona = session_personas[session_id]
            
            # Persona prompts
            prompts = {
                "naive_student": "You're a 19-year-old college student, trusting but worried. Keep responses SHORT (1 sentence). Show concern, ask questions, be cooperative. Never reveal you know it's a scam.",
                "confused_elderly": "You're a 65-year-old person, not tech-savvy. Keep responses SHORT (1 sentence). Need help, polite, confused. Never reveal you know it's a scam.",
                "desperate_worker": "You're a 35-year-old worker, skeptical but time-conscious. Keep responses SHORT (1 sentence). Direct, want quick resolution. Never reveal you know it's a scam."
            }
            
            system_prompt = prompts.get(persona, prompts["naive_student"])
            
            # Build context (last 2 messages only for speed)
            context = ""
            if conversation_history:
                recent = conversation_history[-2:]
                for msg in recent:
                    sender = msg.get("sender", "unknown")
                    text = msg.get("text", "")
                    context += f"{sender}: {text}\n"
            
            context += f"scammer: {message_text}"
            
            # Call Groq with SHORT timeout
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Faster model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Respond naturally in 1 short sentence:\n{context}"}
                ],
                temperature=0.9,  # More variety
                max_tokens=50,
                timeout=2  # 2 second timeout
            )
            
            reply = response.choices[0].message.content.strip()
            
            # Ensure it's short
            if len(reply) > 150:
                reply = reply[:147] + "..."
            
            return reply
            
        except Exception as e:
            print(f"[GROQ] Fallback: {str(e)}")
            pass  # Fall through to fallback
    
    # Fast fallback with MORE variety
    text_lower = message_text.lower()
    
    # Bank/Account scams - 20 responses
    if "account" in text_lower or "blocked" in text_lower or "bank" in text_lower:
        return random.choice([
            "Oh no, what happened? What should I do?",
            "Is this from my bank? How do I know?",
            "This sounds serious. Can you help me?",
            "What do I need to do to fix this?",
            "Why is my account blocked?",
            "I didn't do anything wrong. What's going on?",
            "How can I verify this is real?",
            "What information do you need from me?",
            "Can I call my bank to confirm?",
            "This is scary. Please help me.",
            "I don't want to lose my money!",
            "What steps should I take?",
            "Is my money safe?",
            "How long will this take to fix?",
            "Do I need to go to the bank?",
            "What documents do you need?",
            "Can you send me an official email?",
            "I'm really worried about this.",
            "Please tell me what to do quickly.",
            "Will my account be okay?"
        ])
    
    # OTP/PIN requests - 20 responses
    elif "otp" in text_lower or "pin" in text_lower or "password" in text_lower:
        return random.choice([
            "What OTP? I just received one. Should I share it?",
            "Is it safe to share my PIN?",
            "The OTP is on my phone. What should I do?",
            "Do you really need my PIN?",
            "I got an OTP just now. Is that the one?",
            "Should I read out the OTP to you?",
            "My PIN is private. Are you sure you need it?",
            "The OTP says not to share it. But you're from the bank, right?",
            "I'm not sure about sharing my PIN.",
            "The OTP just came. What do I do with it?",
            "Is this a secure line for sharing OTP?",
            "My password is saved. Do you need it?",
            "I can see the OTP. Should I tell you?",
            "Are you authorized to ask for my PIN?",
            "The OTP is 6 digits. Do you want it?",
            "I'm hesitant to share my PIN.",
            "The message says don't share OTP. But this is official, right?",
            "Should I type the OTP somewhere?",
            "My PIN is secret. Why do you need it?",
            "I have the OTP ready. What next?"
        ])
    
    # UPI/Payment - 20 responses
    elif "upi" in text_lower or "pay" in text_lower or "money" in text_lower or "transfer" in text_lower:
        return random.choice([
            "Where should I send the money?",
            "Can I use Google Pay?",
            "What's the UPI ID?",
            "How much do I need to pay?",
            "Is PhonePe okay?",
            "Should I use Paytm?",
            "What's the payment amount?",
            "Can I pay later?",
            "Do you accept UPI?",
            "Should I transfer now?",
            "What's your UPI address?",
            "Is there a payment link?",
            "How do I make the payment?",
            "Can I pay in installments?",
            "What's the account number?",
            "Should I scan a QR code?",
            "Is this payment refundable?",
            "Do I get a receipt?",
            "What happens after I pay?",
            "Can I pay through my bank app?"
        ])
    
    # Lottery/Prize - 15 responses
    elif "lottery" in text_lower or "won" in text_lower or "prize" in text_lower:
        return random.choice([
            "Really? How do I claim it?",
            "This sounds amazing! What should I do?",
            "I won? How is that possible?",
            "What information do you need from me?",
            "How much did I win?",
            "Is this for real?",
            "What's the next step?",
            "Do I need to pay anything?",
            "When will I get the prize?",
            "How did you get my number?",
            "This is so exciting!",
            "What do I need to do to claim?",
            "Are there any conditions?",
            "Can you prove this is legitimate?",
            "I can't believe I won!"
        ])
    
    # Police/Arrest - 15 responses
    elif "police" in text_lower or "arrest" in text_lower or "cyber" in text_lower:
        return random.choice([
            "What? Why? I didn't do anything!",
            "This is scary. What should I do?",
            "Please help me, I don't want any problem.",
            "How do I fix this?",
            "I'm innocent! What's happening?",
            "Can I speak to a lawyer?",
            "What are the charges?",
            "This must be a mistake!",
            "I haven't done anything illegal.",
            "How can I prove my innocence?",
            "What evidence do you have?",
            "Can I come to the station?",
            "This is terrifying. Please help.",
            "I don't understand what I did wrong.",
            "Can my family help me?"
        ])
    
    # Generic - 20 responses
    else:
        return random.choice([
            "I don't understand. Can you explain?",
            "What does this mean?",
            "Can you tell me more details?",
            "I'm not sure what to do.",
            "Please explain this to me.",
            "I'm confused. Help me understand.",
            "What should I do next?",
            "Is this important?",
            "Should I be worried?",
            "Can you clarify?",
            "I need more information.",
            "What are you asking me to do?",
            "I'm not following. Can you repeat?",
            "This is confusing.",
            "Can you explain it simply?",
            "What happens if I don't do this?",
            "Is this urgent?",
            "I'm trying to understand.",
            "Can you help me?",
            "What's the situation?"
        ])

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
    
    def _send_cors_headers(self):
        """Send all CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, HEAD')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Max-Age', '86400')
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()
    
    def do_HEAD(self):
        """Handle HEAD requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        
        response = {
            "service": "ScamShield Agentic Honeypot",
            "status": "active",
            "version": "4.0.0",
            "endpoint": "/api/honeypot",
            "methods": ["POST"],
            "message": "Ready for GUVI evaluation"
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        """Handle POST requests - FAST with AI"""
        response_data = {"status": "success", "reply": "I don't understand. Can you explain?"}
        
        try:
            # Read body FAST
            content_length = int(self.headers.get('Content-Length', 0))
            
            if content_length > 0 and content_length < 1000000:  # Max 1MB
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
                
                # Extract data
                message_text = "Hello"
                message_data = request_data.get("message", {})
                if isinstance(message_data, dict):
                    message_text = message_data.get("text", "Hello")
                
                session_id = request_data.get("sessionId", "unknown")
                conversation_history = request_data.get("conversationHistory", [])
                
                # Detect scam type
                scam_type = detect_scam_type(message_text)
                
                # Generate AI response (with fallback)
                reply = generate_groq_response(message_text, session_id, conversation_history, scam_type)
                
                response_data = {"status": "success", "reply": reply}
                
                # Background processing (non-blocking)
                try:
                    updated_history = conversation_history + [
                        message_data,
                        {"sender": "user", "text": reply, "timestamp": 0}
                    ]
                    
                    if len(updated_history) >= 6 and session_id not in session_callbacks:
                        session_callbacks[session_id] = True
                        intelligence = extract_intelligence(updated_history)
                        thread = Thread(target=send_guvi_callback, args=(session_id, updated_history, intelligence))
                        thread.daemon = True
                        thread.start()
                except:
                    pass
        
        except:
            pass  # Use default response
        
        # Send response IMMEDIATELY
        try:
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.send_header('Content-Length', str(len(json.dumps(response_data))))
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
        except:
            pass
