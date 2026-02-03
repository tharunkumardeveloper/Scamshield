from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if self.path == '/health':
            response = {
                "status": "healthy",
                "message": "ScamShield API is running on Vercel"
            }
        else:
            response = {
                "service": "ScamShield Honeypot API",
                "status": "active",
                "version": "1.0.0",
                "message": "API is working. Use POST /api/honeypot to test scam detection."
            }
        
        self.wfile.write(json.dumps(response).encode())
        return
    
    def do_POST(self):
        if self.path == '/api/honeypot':
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                request_data = json.loads(post_data.decode('utf-8'))
                
                # Simple response for now
                response = {
                    "status": "success",
                    "scam_detected": True,
                    "confidence_score": 0.85,
                    "scam_type": "detected",
                    "agent_response": "This is a test response from ScamShield API",
                    "conversation_turns": 1,
                    "extracted_intelligence": {
                        "upi_ids": [],
                        "phone_numbers": [],
                        "bank_accounts": [],
                        "phishing_urls": [],
                        "keywords": []
                    },
                    "engagement_metrics": {
                        "conversation_duration_seconds": 0,
                        "scammer_engagement_level": "low",
                        "intelligence_quality": "low"
                    }
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_response = {"error": str(e)}
                self.wfile.write(json.dumps(error_response).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

