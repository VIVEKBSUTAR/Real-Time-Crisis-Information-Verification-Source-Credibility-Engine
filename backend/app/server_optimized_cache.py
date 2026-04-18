"""
Sentinel Protocol - Optimized Backend with In-Memory Embedding Cache
Caches embeddings in memory to avoid regenerating them on every request
"""

import json
import uuid
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import numpy as np

# Import components
from app.dataset_loader import load_dataset, get_dataset
from app.core.semantic_pipeline import semantic_pipeline, initialize_embedding_model, get_embedding
from app.core.advanced_pipeline import AdvancedVerificationPipeline
from app.json_encoder import safe_json_dumps

print("\n🚀 OPTIMIZED ADVANCED MODE - Sentinel Protocol Backend")
print("=" * 60)
print("Pipeline: Input → Normalization → Clustering → Trust →")
print("          NLI → Decision → Alerts → Explanation → Learning")
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

# Global cache for dataset and embeddings
DATASET_READY = False
dataset = None
embeddings_cache = {}  # Cache embeddings in memory
dataset_embeddings = []  # Pre-computed embeddings for full dataset

def ensure_dataset_loaded():
    """Load dataset and pre-compute all embeddings once"""
    global DATASET_READY, dataset, embeddings_cache, dataset_embeddings
    
    if DATASET_READY:
        return True
    
    print("2️⃣  Loading dataset...")
    try:
        if load_dataset():
            dataset = get_dataset()
            DATASET_READY = True
            print(f"   ✅ Dataset loaded: {len(dataset)} claims")
            
            # Pre-compute ALL embeddings (only once)
            print("\n3️⃣  Caching embeddings in memory...")
            print("   ⏳ First request takes longer (computing embeddings)...\n")
            
            for i, item in enumerate(dataset):
                claim_text = item.get("text", "")
                claim_id = item.get("id", f"CLAIM_{i}")
                
                try:
                    # Get embedding (will be cached by model)
                    embedding = get_embedding(claim_text)
                    embeddings_cache[claim_id] = embedding
                    dataset_embeddings.append(embedding)
                    item["embedding"] = embedding  # Store in dataset too
                    
                except Exception as e:
                    print(f"   ⚠️  Failed to embed claim {i}: {str(e)[:50]}")
                    dataset_embeddings.append(np.zeros(384))  # Fallback
                    continue
                
                if (i + 1) % 5000 == 0:
                    print(f"   ✓ Cached {i+1:,}/{len(dataset):,} embeddings...")
            
            print(f"\n   ✅ Cached {len(embeddings_cache):,} embeddings in memory")
            print(f"   💾 Memory usage: {len(embeddings_cache) * 384 * 4 / 1024 / 1024:.1f}MB\n")
            return True
            
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
    
    return False

# Initialize advanced pipeline
pipeline = AdvancedVerificationPipeline()

class AdvancedVerificationHandler(BaseHTTPRequestHandler):
    """Handle advanced verification requests"""
    
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
                "app": "Sentinel Protocol (Optimized)",
                "mode": "clustering + trust + alerts + Bayesian learning",
                "embedding_ready": EMBEDDING_READY,
                "dataset_ready": DATASET_READY,
                "cached_embeddings": len(embeddings_cache),
                "pipeline_stages": [
                    "normalization",
                    "embedding_generation",
                    "clustering",
                    "signal_extraction",
                    "trust_verification",
                    "nli_reasoning",
                    "verdict_generation",
                    "alert_routing",
                    "explanation_generation",
                    "bayesian_learning"
                ]
            }
            self.wfile.write(safe_json_dumps(response).encode())
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
                
                # Lazy load dataset (only once on first request)
                if not DATASET_READY:
                    if not ensure_dataset_loaded():
                        self.send_error_response(503, "Dataset not available")
                        return
                
                print(f"📊 Processing claim: {claim[:50]}...")
                
                # Get user embedding (fast - model cached)
                user_embedding = get_embedding(claim)
                
                # Use pre-cached dataset embeddings (instant!)
                if not dataset_embeddings:
                    self.send_error_response(503, "Embeddings not ready")
                    return
                
                # Run advanced pipeline (uses cached embeddings)
                result = pipeline.process_claim(
                    user_claim=claim,
                    user_embedding=user_embedding,
                    dataset_embeddings=dataset_embeddings,
                    dataset_items=list(dataset)
                )
                
                # Format response
                response = {
                    "claim": claim,
                    "verdict": result.get("verdict", "UNCERTAIN"),
                    "confidence": float(result.get("confidence", 0.5)),
                    "clustering": result.get("clustering", {}),
                    "trust_analysis": result.get("trust_analysis", {}),
                    "nli_scores": result.get("nli_scores", {}),
                    "alerts": result.get("alerts", {}),
                    "explanation": result.get("explanation", ""),
                    "learning_state": result.get("learning_state", {}),
                    "pipeline": result.get("pipeline", {})
                }
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(safe_json_dumps(response).encode())
                print(f"   ✅ Response sent\n")
                
            except json.JSONDecodeError:
                self.send_error_response(400, "Invalid JSON")
            except Exception as e:
                print(f"   ❌ Error: {e}\n")
                import traceback
                traceback.print_exc()
                self.send_error_response(500, f"Error: {str(e)[:100]}")
        
        else:
            self.send_response(404)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
    
    def send_error_response(self, code, message):
        """Send error response"""
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        response = {"error": message, "code": code}
        self.wfile.write(safe_json_dumps(response).encode())

def run_server(port=8000):
    """Start the HTTP server"""
    print("3️⃣  Starting HTTP server on port 8000...\n")
    print("📍 Endpoints:")
    print("   • GET  http://localhost:8000/health")
    print("   • POST http://localhost:8000/analyze_claim\n")
    print("✨ Advanced pipeline ready!")
    print("=" * 60 + "\n")
    
    server_address = ("", port)
    httpd = HTTPServer(server_address, AdvancedVerificationHandler)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
