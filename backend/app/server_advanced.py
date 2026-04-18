"""
Sentinel Protocol - Advanced Mode Server
Full workflow: Input → Normalization → Clustering → Trust → NLI → Decision → Alerts → Explanation → Learning
"""

import json
import uuid
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import numpy as np

# Import components
from app.dataset_loader import load_dataset, get_dataset
from app.core.semantic_pipeline import semantic_pipeline, initialize_embedding_model
from app.core.advanced_pipeline import AdvancedVerificationPipeline

print("\n🚀 ADVANCED MODE - Sentinel Protocol Backend")
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

# Load dataset
DATASET_READY = False
dataset = []

def ensure_dataset_loaded():
    global DATASET_READY, dataset
    if DATASET_READY:
        return True
    
    print("2️⃣  Loading dataset...")
    try:
        if load_dataset():
            dataset = get_dataset()
            DATASET_READY = True
            print(f"   ✅ Dataset loaded: {len(dataset)} claims\n")
            return True
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
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
                "app": "Sentinel Protocol (Advanced)",
                "mode": "clustering + trust + alerts + Bayesian learning",
                "embedding_ready": EMBEDDING_READY,
                "dataset_ready": DATASET_READY,
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
                
                print(f"📊 Processing claim: {claim[:50]}...")
                
                # Get user embedding
                from app.core.semantic_pipeline import get_embedding
                user_embedding = get_embedding(claim)
                
                # Get dataset embeddings
                dataset_embeddings = []
                for item in dataset:
                    if "embedding" in item:
                        dataset_embeddings.append(item["embedding"])
                    else:
                        # Compute embedding if not cached
                        emb = get_embedding(item.get("text", ""))
                        dataset_embeddings.append(emb)
                        item["embedding"] = emb
                
                # Run advanced pipeline
                result = pipeline.process_claim(
                    user_claim=claim,
                    user_embedding=user_embedding,
                    dataset_embeddings=dataset_embeddings,
                    dataset_items=dataset
                )
                
                # Format response
                response = {
                    "id": str(uuid.uuid4()),
                    "claim": claim,
                    "verdict": result["verdict"]["verdict"],
                    "confidence": round(result["verdict"]["confidence"], 3),
                    
                    # Clustering insights
                    "clustering": {
                        "cluster_count": result["clustering"]["cluster_count"],
                        "total_similar_groups": result["clustering"]["cluster_count"]
                    },
                    
                    # Trust analysis
                    "trust_analysis": {
                        "average_trust_score": round(
                            np.mean([s["score"] for s in result["trust_scores"].values()]),
                            3
                        ),
                        "consensus_strength": round(
                            np.mean([s["label_agreement"] for s in result["trust_scores"].values()]),
                            3
                        )
                    },
                    
                    # NLI scores
                    "nli_scores": {
                        "entailment": round(result["verdict"].get("entailment", 0), 3),
                        "contradiction": round(result["verdict"].get("contradiction", 0), 3)
                    },
                    
                    # Alert system
                    "alerts": {
                        "high_priority": [a for a in result["alerts"].get("admin_notifications", [])],
                        "flagged_for_review": result["alerts"].get("flagged_for_review", []),
                        "total_alerts": len(result["alerts"].get("logged", []))
                    },
                    
                    # Explanation
                    "explanation": result["explanation"],
                    
                    # Bayesian learning state
                    "learning_state": result["bayesian_state"],
                    
                    # Pipeline metadata
                    "pipeline": {
                        "mode": "advanced",
                        "stages": [
                            "✅ normalization",
                            "✅ embedding",
                            "✅ clustering",
                            "✅ trust_scoring",
                            "✅ nli_reasoning",
                            "✅ verdict_generation",
                            "✅ alert_routing",
                            "✅ explanation",
                            "✅ bayesian_state"
                        ]
                    },
                    
                    "timestamp": datetime.now().isoformat()
                }
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(response, indent=2, default=str).encode())
                
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
    print(f"\n3️⃣  Starting HTTP server on port {port}...\n")
    print("📍 Endpoints:")
    print(f"   • GET  http://localhost:{port}/health")
    print(f"   • POST http://localhost:{port}/analyze_claim")
    print("\n✨ Advanced pipeline ready!")
    print("=" * 60 + "\n")
    
    server = HTTPServer(("localhost", port), AdvancedVerificationHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped")
        server.server_close()

if __name__ == "__main__":
    run_server()
