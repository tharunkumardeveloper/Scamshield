from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "healthy", "message": "ScamShield API is running"}
            self.wfile.write(json.dumps(response).encode())
            return
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {
            "service": "ScamShield Honeypot API",
            "status": "active",
            "version": "1.0.0"
        }
        self.wfile.write(json.dumps(response).encode())
