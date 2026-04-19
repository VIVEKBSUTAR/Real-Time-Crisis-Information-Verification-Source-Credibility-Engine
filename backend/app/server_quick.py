"""
Sentinel Protocol Backend - Quick Start Version
Minimal dependencies, semantic pipeline ready immediately
"""

import json
import uuid
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from difflib import SequenceMatcher

# Import pipeline components
from app.dataset_loader import load_dataset, get_dataset
from app.core.semantic_pipeline import semantic_pipeline, initialize_embedding_model

print("\n🚀 QUICK START - Sentinel Protocol Backend")
print("=" * 50)

# Load embedding model (downloads ~110MB)
print("1️⃣  Loading embedding model...")
try:
    initialize_embedding_model("all-MiniLM-L6-v2")
    EMBEDDING_READY = True
    print("   ✅ Embedding model loaded\n")
except Exception as e:
    print(f"   ❌ Error: {e}\n")
    EMBEDDING_READY = False

# Load dataset in background or on first request
DATASET_READY = False
dataset = []

def ensure_dataset_loaded():
    """Lazy load dataset on first request"""
    global DATASET_READY, dataset
    if DATASET_READY:
        return True
    
    print("2️⃣  Loading dataset (first request)...")
    try:
        if load_dataset():
            dataset = get_dataset()
            DATASET_READY = True
            print(f"   ✅ Dataset loaded: {len(dataset)} claims\n")
            return True
    except Exception as e:
        print(f"   ❌ Dataset error: {e}\n")
    return False


class VerificationHandler(BaseHTTPRequestHandler):
    """Handle HTTP requests"""
    
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
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            response = {
                "status": "healthy",
                "app": "Sentinel Protocol (Quick Start)",
                "version": "0.3.1-quick",
                "embedding_ready": EMBEDDING_READY,
                "dataset_ready": DATASET_READY,
                "mode": "Semantic Pipeline + Mock NLI"
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        self.send_response(404)
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
                
                # Lazy load dataset
                if not DATASET_READY:
                    if not ensure_dataset_loaded():
                        self.send_error_response(503, "Dataset not available")
                        return
                
                # Run semantic pipeline
                similar_results, stats = semantic_pipeline(claim, dataset, k=5)

                # semantic_pipeline expects per-item embeddings, but quick mode dataset
                # may only have raw text entries. Fall back to lexical matching.
                if not similar_results and hasattr(dataset, "find_similar"):
                    claim_lower = claim.lower()
                    lexical = dataset.find_similar(claim, threshold=0.2, limit=5)
                    similar_results = [
                        {
                            "text": row.get("text", ""),
                            "label": int(row.get("label", 0) or 0),
                            "similarity": float(
                                SequenceMatcher(
                                    None,
                                    claim_lower,
                                    str(row.get("text", "")).lower(),
                                ).ratio()
                            ),
                            "source": str(row.get("source", "Dataset Source")),
                        }
                        for row in lexical
                        if str(row.get("text", "")).strip()
                    ]
                
                # Simple aggregation (without heavy NLI)
                if similar_results:
                    # Count how many dataset claims say TRUE vs FALSE
                    true_count = sum(1 for r in similar_results if r.get("label") == 1)
                    false_count = len(similar_results) - true_count
                    
                    # Determine verdict
                    if true_count > false_count:
                        verdict = "VERIFIED"
                        confidence = min(0.95, true_count / len(similar_results) + 0.2)
                    elif false_count > true_count:
                        verdict = "FALSE"
                        confidence = min(0.95, false_count / len(similar_results) + 0.2)
                    else:
                        verdict = "UNCERTAIN"
                        confidence = 0.5
                else:
                    verdict = "UNCERTAIN"
                    confidence = 0.0
                
                response = {
                    "id": str(uuid.uuid4()),
                    "claim": claim,
                    "verdict": verdict,
                    "confidence": round(confidence, 2),
                    "explanation": f"Based on {len(similar_results)} similar claims in dataset",
                    "sources": [
                        {
                            "text": row.get("text", ""),
                            "similarity": float(row.get("similarity", 0.0) or 0.0),
                            "label": "TRUE" if int(row.get("label", 0) or 0) == 1 else "FALSE",
                            "relation": "supports" if int(row.get("label", 0) or 0) == 1 else "contradicts",
                            "score": float(row.get("similarity", 0.0) or 0.0),
                            "source": str(row.get("source", "Dataset Source")),
                        }
                        for row in similar_results
                    ],
                    "evidence": {
                        "similar_claims_found": len(similar_results),
                        "confidence_percentage": round(confidence * 100)
                    },
                    "pipeline_status": {
                        "step_1_semantic_search": "✅ Complete",
                        "step_2_nli_inference": "✅ Mock mode",
                        "step_3_aggregation": "✅ Complete"
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(response, indent=2).encode())
                
            except Exception as e:
                self.send_error_response(500, str(e))
        else:
            self.send_response(404)
            self.end_headers()
    
    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode())


def run_server(port=8000):
    print(f"3️⃣  Starting HTTP server on port {port}...\n")
    print("📍 Endpoints:")
    print(f"   • GET  http://localhost:{port}/health")
    print(f"   • POST http://localhost:{port}/analyze_claim")
    print("\n✨ Ready to verify claims!")
    print("=" * 50 + "\n")
    
    server = HTTPServer(("localhost", port), VerificationHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped")
        server.server_close()

if __name__ == "__main__":
    run_server()
