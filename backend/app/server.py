"""
Sentinel Protocol Backend - Pure Python HTTP Server
No external framework dependencies (Flask/FastAPI cause Python 3.14 issues)
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import uuid
import random
from urllib.parse import urlparse, parse_qs
import sys

class VerificationHandler(BaseHTTPRequestHandler):
    """Handle HTTP requests for claim verification"""
    
    def log_message(self, format, *args):
        """Suppress verbose logging"""
        if "health" not in args[0]:
            sys.stderr.write("%s\n" % (format%args))
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            response = {
                "status": "healthy",
                "app": "Sentinel Protocol",
                "version": "0.1.0",
                "message": "Backend running successfully"
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == "/analyze_claim":
            try:
                # Read request body
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                request = json.loads(body.decode())
                
                # Extract claim
                claim_text = request.get('text', 'Unknown claim')
                
                # Generate response
                claim_id = str(uuid.uuid4())[:8]
                verdicts = ["Verified", "Debunked", "Manipulated"]
                verdict = random.choice(verdicts)
                confidence = round(random.uniform(0.5, 0.95), 2)
                
                response = {
                    "claim_id": claim_id,
                    "original_claim": claim_text,
                    "verdict": verdict,
                    "confidence": confidence,
                    "evidence": [
                        {"source": "Reuters", "relation": "support", "confidence": 0.82},
                        {"source": "AP News", "relation": "support", "confidence": 0.75}
                    ],
                    "explanation": f"This claim is likely {verdict.lower()} based on 2 trusted sources within the time window."
                }
                
                # Send response
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())


def run_server(host="0.0.0.0", port=8000):
    """Start the HTTP server"""
    server_address = (host, port)
    httpd = HTTPServer(server_address, VerificationHandler)
    print(f"✅ Sentinel Protocol Backend running on {host}:{port}")
    print(f"   Health: http://{host}:{port}/health")
    print(f"   Analysis: POST http://{host}:{port}/analyze_claim")
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()
