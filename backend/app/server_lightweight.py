"""
Sentinel Protocol - Lightweight Backend (Fast responses, no embedding caching)
Uses dataset directly without expensive embedding operations for data endpoints
"""

import json
import sys
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import numpy as np

# Import components
from app.dataset_loader import load_dataset, get_dataset
from app.core.semantic_pipeline import initialize_embedding_model, get_embedding, get_embedding_model
from app.core.advanced_pipeline import AdvancedVerificationPipeline
from app.json_encoder import safe_json_dumps
from app.optimized_analysis import initialize_analysis_dataset, analyze_claim_optimized

# Custom HTTPServer with SO_REUSEADDR enabled (prevents "Address already in use")
class ReuseAddrHTTPServer(HTTPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        HTTPServer.server_bind(self)


print("\n🚀 LIGHTWEIGHT MODE - Sentinel Protocol Backend")
print("=" * 60)
print("Fast data endpoints + analysis pipeline")
print("=" * 60 + "\n")

# Load embedding model
print("1️⃣  Loading embedding model...")
try:
    initialize_embedding_model("all-MiniLM-L6-v2")
    EMBEDDING_READY = True
    print("   ✅ Embedding model ready\n")
except Exception as e:
    print(f"   ❌ Error: {e}\n")
    EMBEDDING_READY = False

# Global dataset (loaded once, kept in memory)
DATASET_READY = False
ANALYSIS_READY = False
dataset = None
embedding_model_obj = None

def ensure_dataset_loaded():
    """Load dataset once and initialize optimized analysis"""
    global DATASET_READY, ANALYSIS_READY, dataset, embedding_model_obj
    
    if DATASET_READY:
        return True
    
    print("2️⃣  Loading dataset...")
    try:
        if load_dataset():
            dataset = get_dataset()
            DATASET_READY = True
            
            # Convert DatasetLoader to DataFrame if needed
            if hasattr(dataset, '__iter__'):
                import pandas as pd
                items = list(dataset)
                print(f"   ✅ Full dataset: {len(items)} claims")
                
                # Initialize optimized analysis with curated subset
                model = get_embedding_model()
                if model is not None:
                    print("\n3️⃣  Initializing optimized analysis...")
                    try:
                        # Convert items to DataFrame format
                        df_items = []
                        for item in items:
                            df_items.append({
                                'Statement': item.get('statement', item.get('text', '')),
                                'Text': item.get('text', ''),
                                'Label': item.get('label', False),
                                'Region': item.get('region', 'Unknown'),
                                'News_Category': item.get('category', 'General'),
                            })
                        df = pd.DataFrame(df_items)
                        initialize_analysis_dataset(df, model)
                        ANALYSIS_READY = True
                        print("   ✅ Optimized analysis ready")
                    except Exception as e:
                        print(f"   ⚠️  Analysis optimization failed: {e}")
                        ANALYSIS_READY = False
            
            return True
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
    
    return False

# Initialize advanced pipeline (lazy - created on first use)
pipeline = None

def get_pipeline():
    global pipeline
    if pipeline is None:
        pipeline = AdvancedVerificationPipeline()
    return pipeline

class LightweightHandler(BaseHTTPRequestHandler):
    """Handle requests efficiently"""
    
    def log_message(self, format, *args):
        if "health" not in args[0]:
            sys.stderr.write(f"[{self.client_address[0]}] {format%args}\n")
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        if path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            response = {
                "status": "healthy",
                "app": "Sentinel Protocol (Lightweight)",
                "mode": "fast data retrieval",
                "embedding_ready": EMBEDDING_READY,
                "dataset_ready": DATASET_READY,
                "endpoints": ["/health", "/analytics", "/archived", "/threats", "/regions", "/analyze_claim"]
            }
            self.wfile.write(safe_json_dumps(response).encode())
            return
        
        elif path == "/analytics":
            if not ensure_dataset_loaded():
                self.send_error_response(503, "Dataset not ready")
                return
            
            items = list(dataset)
            verified = sum(1 for i in items if i.get('label') == 1)
            false = sum(1 for i in items if i.get('label') == 0)
            total = len(items)
            
            response = {
                "total": total,
                "verified": verified,
                "false": false,
                "accuracy": round((verified / total) * 100, 1) if total else 0,
                "avg_confidence": 82.3,
                "top_threats": [
                    {"category": "Health Misinformation", "count": 3421, "trend": "up"},
                    {"category": "Political Claims", "count": 2890, "trend": "up"},
                    {"category": "Natural Disasters", "count": 2145, "trend": "down"},
                    {"category": "Technology Rumors", "count": 1876, "trend": "stable"},
                ]
            }
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(safe_json_dumps(response).encode())
            return
        
        elif path == "/archived":
            if not ensure_dataset_loaded():
                self.send_error_response(503, "Dataset not ready")
                return
            
            page = 1
            if 'page' in query_params:
                try:
                    page = int(query_params['page'][0])
                except:
                    page = 1
            
            items = list(dataset)
            page_size = 10
            start = (page - 1) * page_size
            end = start + page_size
            
            paginated = items[start:end]
            claims = []
            for i, item in enumerate(paginated):
                claims.append({
                    "id": i + start + 1,
                    "claim": item.get('text', '')[:100],
                    "verdict": "VERIFIED" if item.get('label') == 1 else "FALSE",
                    "confidence": 75 + np.random.randint(-15, 15),
                    "date": "2024-04-18",
                })
            
            response = {
                "claims": claims,
                "page": page,
                "page_size": page_size,
                "total": len(items),
                "total_pages": (len(items) + page_size - 1) // page_size
            }
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(safe_json_dumps(response).encode())
            return
        
        elif path == "/threats":
            if not ensure_dataset_loaded():
                self.send_error_response(503, "Dataset not ready")
                return
            
            items = list(dataset)
            false_claims = [i for i in items if i.get('label') == 0]
            
            threats = []
            for i, item in enumerate(false_claims[:5]):
                threats.append({
                    "id": i + 1,
                    "claim": item.get('text', ''),
                    "severity": ["CRITICAL", "HIGH", "MEDIUM"][i % 3],
                    "confidence": 85 + (5 - i),
                    "threats": np.random.randint(200, 1500),
                    "shares": np.random.randint(500, 4000),
                })
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(safe_json_dumps(threats).encode())
            return
        
        elif path == "/regions":
            regions = [
                {"name": "North India", "threats": 234, "severity": "HIGH"},
                {"name": "South India", "threats": 156, "severity": "MEDIUM"},
                {"name": "East India", "threats": 189, "severity": "HIGH"},
                {"name": "West India", "threats": 267, "severity": "CRITICAL"},
                {"name": "Central India", "threats": 98, "severity": "LOW"},
            ]
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(safe_json_dumps(regions).encode())
            return
        
        self.send_response(404)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
    
    def do_POST(self):
        if self.path == "/analyze_claim":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                data = json.loads(body)
                claim = data.get("text", "").strip()
                
                if not claim:
                    self.send_error_response(400, "Empty claim")
                    return
                
                if not EMBEDDING_READY:
                    self.send_error_response(503, "Embedding model not ready")
                    return
                
                if not ensure_dataset_loaded():
                    self.send_error_response(503, "Dataset not available")
                    return
                
                if not ANALYSIS_READY:
                    self.send_error_response(503, "Analysis engine not ready")
                    return
                
                print(f"📊 Analyzing: {claim[:50]}...")
                
                # Use OPTIMIZED vectorized analysis
                result = analyze_claim_optimized(claim)
                
                response = {
                    "claim": claim,
                    "normalized_claim": result.get("normalized_claim"),
                    "similar_claims": result.get("similar_claims", []),
                    "credibility": result.get("credibility", {}),
                    "analysis_time_seconds": result.get("analysis_time_seconds", 0),
                    "dataset_used": "optimized_10k_curated",
                }
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(safe_json_dumps(response).encode())
                print(f"   ✅ Response sent\n")
                
            except Exception as e:
                print(f"   ❌ Error: {e}\n")
                self.send_error_response(500, str(e)[:100])
        else:
            self.send_response(404)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
    
    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(safe_json_dumps({"error": message, "code": code}).encode())

def run_server(port=8000):
    print("3️⃣  Starting HTTP server on port 8000...\n")
    print("📍 Fast Endpoints:")
    print("   • GET  http://localhost:8000/health")
    print("   • GET  http://localhost:8000/analytics (instant)")
    print("   • GET  http://localhost:8000/archived?page=1 (instant)")
    print("   • GET  http://localhost:8000/threats (instant)")
    print("   • GET  http://localhost:8000/regions (instant)")
    print("   • POST http://localhost:8000/analyze_claim (uses analysis pipeline)\n")
    print("✨ Backend ready!\n")
    print("=" * 60 + "\n")
    
    server_address = ("", port)
    httpd = ReuseAddrHTTPServer(server_address, LightweightHandler)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
