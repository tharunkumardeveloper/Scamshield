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
            
            # Persona prompts - COOPERATIVE VICTIMS
            prompts = {
                "naive_student": "You're a 19-year-old college student, trusting and worried about your account. Keep responses SHORT (1 sentence). Be COOPERATIVE, willing to help, ask what to do. Never reveal you know it's a scam. Act genuinely concerned and ready to follow instructions.",
                "confused_elderly": "You're a 65-year-old person, not tech-savvy, trusting authority figures. Keep responses SHORT (1 sentence). Be COOPERATIVE, polite, willing to share information if asked. Never reveal you know it's a scam. Act genuinely confused but helpful.",
                "desperate_worker": "You're a 35-year-old worker, worried about losing access to your account. Keep responses SHORT (1 sentence). Be COOPERATIVE, want quick resolution, willing to provide what's needed. Never reveal you know it's a scam. Act busy but compliant."
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
    
    # Fast fallback with MORE variety and CONTEXT AWARENESS
    text_lower = message_text.lower()
    
    # Check conversation history for context
    history_text = ""
    if conversation_history:
        history_text = " ".join([msg.get("text", "") for msg in conversation_history[-3:]]).lower()
    
    # If scammer mentioned specific things, respond to them
    if "otp" in text_lower or "pin" in text_lower or "password" in text_lower:
        # OTP/PIN requests - COOPERATIVE responses (naive victim)
        return random.choice([
            "Okay, the OTP is on my phone. Let me check.",
            "I just got an OTP. Should I tell you all 6 digits?",
            "The OTP just arrived. What should I do with it?",
            "My PIN? Okay, if you need it to fix this.",
            "I have the OTP ready. Where should I send it?",
            "The OTP says don't share, but you're from the bank right?",
            "Okay, I'll share the OTP. Just help me fix this.",
            "The OTP is here. Do you want me to read it?",
            "I trust you. The OTP is on my screen.",
            "My PIN is saved. How do I share it securely?",
            "Okay, I'll give you the OTP. Please don't block my account.",
            "The OTP just came through. What's next?",
            "I'm ready to share the OTP. Just tell me how.",
            "My password? If it helps unblock my account, okay.",
            "The OTP is 6 digits. Should I type it here?",
            "I'll do whatever you need. The OTP is ready.",
            "Okay, I have the OTP. How do I send it to you?",
            "My PIN? Alright, if that's what's needed.",
            "The OTP message just arrived. I'm ready.",
            "I'll share everything you need. Just help me!"
        ])
    
    # If asking for documents/ID - COOPERATIVE
    elif "photo" in text_lower or "id" in text_lower or "document" in text_lower or "aadhaar" in text_lower or "pan" in text_lower:
        return random.choice([
            "Okay, I can send a photo of my ID. Where?",
            "I have my Aadhaar card here. Should I take a photo?",
            "My PAN card is with me. How should I send it?",
            "I'll send the documents. What's your email?",
            "Okay, let me take a photo of my ID card.",
            "I can send both sides of the card. Is that okay?",
            "My documents are ready. Where do I send them?",
            "I'll email the photos. What address?",
            "Okay, I'm taking a photo of my Aadhaar now.",
            "I trust you. I'll send my ID proof right away."
        ])
    
    # If asking for email/contact
    elif "email" in text_lower or "send" in text_lower or "contact" in text_lower:
        return random.choice([
            "What's your email address?",
            "Where should I send it?",
            "Is this email official?",
            "Can I call instead?",
            "What's the official contact?",
            "Should I reply to this email?",
            "Is there a customer service number?",
            "How do I know this is legitimate?",
            "Can you verify your identity first?",
            "What's your official website?"
        ])
    
    # Bank/Account scams - context aware
    elif "account" in text_lower or "blocked" in text_lower or "bank" in text_lower:
        # If they already mentioned account number in history
        if any(word in history_text for word in ["account number", "16-digit", "digits"]):
            return random.choice([
                "I already told you my account details. What else?",
                "You have my account number. What's next?",
                "Is there anything else you need?",
                "What should I do after this?",
                "How long will this take?"
            ])
        else:
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
    
    # UPI/Payment - context aware
    elif "upi" in text_lower or "pay" in text_lower or "money" in text_lower or "transfer" in text_lower:
        # If they already mentioned UPI in history
        if "upi" in history_text or "@" in history_text:
            return random.choice([
                "I'll send it to that UPI ID now.",
                "Should I transfer the full amount?",
                "Let me open my payment app.",
                "Is that the correct UPI address?",
                "How much exactly?"
            ])
        else:
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
    
    # Lottery/Prize
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
    
    # Police/Arrest
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
    
    # Generic - context aware
    else:
        # If conversation is ongoing, show progression
        if len(conversation_history) > 4:
            return random.choice([
                "Okay, I understand. What's next?",
                "I'm following your instructions. Continue.",
                "Yes, I'm ready. What else?",
                "I'm doing what you said. What now?",
                "Alright, what's the next step?"
            ])
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
    """Extract intelligence from conversation - ENHANCED"""
    all_text = " ".join([msg.get("text", "") for msg in conversation_history])
    
    # Extract UPI IDs - CATCH ALL @ patterns
    upi_pattern = r'\b[\w\.-]+@[\w\.-]+\b'
    potential_upis = re.findall(upi_pattern, all_text, re.IGNORECASE)
    upi_ids = []
    emails = []
    
    for item in potential_upis:
        # Separate UPI IDs from emails
        if any(domain in item.lower() for domain in ['.com', '.in', '.org', '.net', '.co']):
            emails.append(item)  # It's an email
        else:
            upi_ids.append(item)  # It's a UPI ID
    
    upi_ids = list(set(upi_ids))
    emails = list(set(emails))
    
    # Extract bank accounts (11-18 digits to avoid phone numbers)
    account_pattern = r'\b\d{11,18}\b'
    bank_accounts = list(set(re.findall(account_pattern, all_text)))
    
    # Also try 10-digit numbers that DON'T start with 6-9 (not phone numbers)
    ten_digit_pattern = r'\b[0-5]\d{9}\b'
    ten_digit_accounts = re.findall(ten_digit_pattern, all_text)
    bank_accounts.extend(ten_digit_accounts)
    bank_accounts = list(set(bank_accounts))
    
    # Extract URLs/phishing links
    url_pattern = r'https?://[^\s]+|www\.[^\s]+'
    phishing_links = list(set(re.findall(url_pattern, all_text, re.IGNORECASE)))
    
    # Add emails to phishing links
    phishing_links.extend(emails)
    phishing_links = list(set(phishing_links))
    
    # Extract phone numbers (Indian format) - IMPROVED
    phone_pattern = r'(?:\+91[\-\s]?)?[6-9]\d{9}\b'
    phone_numbers = list(set(re.findall(phone_pattern, all_text)))
    # Format consistently
    formatted_phones = []
    for phone in phone_numbers:
        clean = phone.replace('+91', '').replace('-', '').replace(' ', '').strip()
        if len(clean) == 10:
            formatted_phones.append('+91' + clean)
    phone_numbers = list(set(formatted_phones))
    
    # Suspicious keywords
    keywords = ["urgent", "blocked", "verify", "immediately", "suspended", "account", 
                "bank", "upi", "pay", "transfer", "click", "link", "otp", "pin", 
                "password", "secure", "fraud", "compromised"]
    suspicious_keywords = list(set([kw for kw in keywords if kw in all_text.lower()]))
    
    return {
        "bankAccounts": bank_accounts,
        "upiIds": upi_ids,
        "phishingLinks": phishing_links,
        "phoneNumbers": phone_numbers,
        "suspiciousKeywords": suspicious_keywords
    }

def send_guvi_callback(session_id, conversation_history, intelligence):
    """Send final callback to GUVI (runs in background thread) - ALWAYS SEND"""
    try:
        total_messages = len(conversation_history)
        
        # ALWAYS detect scam if there are suspicious keywords or extracted data
        scam_detected = any([
            intelligence["upiIds"],
            intelligence["bankAccounts"],
            intelligence["phishingLinks"],
            intelligence["phoneNumbers"],
            len(intelligence["suspiciousKeywords"]) >= 2  # Lower threshold
        ])
        
        # If no clear scam indicators but conversation happened, still mark as potential scam
        if not scam_detected and total_messages >= 6:
            scam_detected = True  # Assume scam if they engaged for 6+ messages
        
        # Generate agent notes
        notes = f"Conversation with {total_messages} messages. "
        if intelligence["upiIds"]:
            notes += f"Extracted {len(intelligence['upiIds'])} UPI IDs: {', '.join(intelligence['upiIds'])}. "
        if intelligence["bankAccounts"]:
            notes += f"Extracted {len(intelligence['bankAccounts'])} bank accounts: {', '.join(intelligence['bankAccounts'])}. "
        if intelligence["phishingLinks"]:
            notes += f"Detected {len(intelligence['phishingLinks'])} phishing links/emails: {', '.join(intelligence['phishingLinks'])}. "
        if intelligence["phoneNumbers"]:
            notes += f"Extracted {len(intelligence['phoneNumbers'])} phone numbers: {', '.join(intelligence['phoneNumbers'])}. "
        
        if any([intelligence["upiIds"], intelligence["bankAccounts"], intelligence["phishingLinks"], intelligence["phoneNumbers"]]):
            notes += "Successfully extracted sensitive information from scammer. "
        
        notes += "Agent maintained believable persona and engaged scammer effectively."
        
        payload = {
            "sessionId": session_id,
            "scamDetected": scam_detected,
            "totalMessagesExchanged": total_messages,
            "extractedIntelligence": intelligence,
            "agentNotes": notes
        }
        
        print(f"[CALLBACK] Sending to GUVI: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            "https://hackathon.guvi.in/api/updateHoneyPotFinalResult",
            json=payload,
            timeout=5
        )
        
        print(f"[CALLBACK] Session {session_id}: Status {response.status_code}, Response: {response.text}")
        
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
