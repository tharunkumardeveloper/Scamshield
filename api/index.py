from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.request_models import HoneypotRequest, Message
from agents.scam_detector import ScamDetector
from agents.persona_agent import PersonaAgent
from agents.intelligence_extractor import IntelligenceExtractor
from services.guvi_callback import GuviCallbackService

# Initialize agents
scam_detector = ScamDetector()
persona_agent = PersonaAgent(api_key=os.getenv("GROQ_API_KEY", ""))
intelligence_extractor = IntelligenceExtractor()
guvi_callback = GuviCallbackService()

# Simple session tracking
session_data = {}

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
        
        if self.path == '/health':
            response = {
                "status": "healthy",
                "message": "ScamShield API is running"
            }
        else:
            response = {
                "service": "ScamShield Honeypot API",
                "status": "active",
                "version": "2.0.0",
                "competition": "GUVI Agentic Honey-Pot Challenge",
                "endpoint": "POST /api/honeypot"
            }
        
        self.wfile.write(json.dumps(response).encode())
        return
    
    def do_POST(self):
        if self.path == '/api/honeypot':
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
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                request_data = json.loads(post_data.decode('utf-8'))
                
                # Parse request
                session_id = request_data.get("sessionId")
                message_data = request_data.get("message", {})
                history_data = request_data.get("conversationHistory", [])
                
                # Convert to Message objects
                current_message = Message(**message_data)
                history = [Message(**msg) for msg in history_data]
                
                # Step 1: Detect scam
                scam_analysis = scam_detector.analyze(
                    message_text=current_message.text,
                    history=history
                )
                
                # Step 2: Generate response (synchronous version for serverless)
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                agent_reply = loop.run_until_complete(
                    persona_agent.generate_response(
                        message_text=current_message.text,
                        session_id=session_id,
                        history=history,
                        scam_detected=scam_analysis["detected"]
                    )
                )
                loop.close()
                
                # Step 3: Update history
                updated_history = history + [
                    current_message,
                    Message(sender="user", text=agent_reply, timestamp=current_message.timestamp)
                ]
                
                # Step 4: Extract intelligence
                extracted_intel = intelligence_extractor.extract(updated_history)
                
                # Step 5: Track session
                if session_id not in session_data:
                    session_data[session_id] = {
                        "scam_detected": scam_analysis["detected"],
                        "message_count": 0
                    }
                session_data[session_id]["message_count"] = len(updated_history)
                
                # Step 6: Check if should send final callback
                should_end = guvi_callback.should_end_conversation(
                    history_length=len(updated_history),
                    intelligence=extracted_intel,
                    scam_detected=scam_analysis["detected"]
                )
                
                if should_end and scam_analysis["detected"]:
                    agent_notes = f"Scam type: {scam_analysis.get('scam_type', 'unknown')}. "
                    agent_notes += f"Engagement: {len(updated_history)} messages. "
                    agent_notes += "Intelligence extracted successfully."
                    
                    # Send callback (synchronous)
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(
                        guvi_callback.send_final_result(
                            session_id=session_id,
                            scam_detected=True,
                            total_messages=len(updated_history),
                            intelligence=extracted_intel,
                            agent_notes=agent_notes
                        )
                    )
                    loop.close()
                
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
                error_response = {"error": str(e), "status": "error"}
                self.wfile.write(json.dumps(error_response).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

