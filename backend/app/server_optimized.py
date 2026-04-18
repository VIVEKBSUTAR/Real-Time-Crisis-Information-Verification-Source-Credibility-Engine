"""
Sentinel Protocol Backend - Optimized Semantic Pipeline (No BART Download)

Complete claim verification pipeline:
1. Semantic Processing (normalize → embed → similarity search)
2. NLI Inference (using mock mode to avoid 1.63GB model download)
3. Post-NLI Aggregation (verdict generation)

This version prioritizes fast startup over heavy model loading.
The semantic similarity search is the main intelligence here.
"""

import json
import uuid
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

# Import pipeline components
from app.dataset_loader import load_dataset, get_dataset
from app.core.semantic_pipeline import semantic_pipeline, initialize_embedding_model

print("🚀 Initializing Sentinel Protocol Backend (Optimized)...")

# Load embedding model (downloads ~110MB)
print("📊 Loading embedding model...")
try:
    initialize_embedding_model("all-MiniLM-L6-v2")
    EMBEDDING_READY = True
    print("✅ Embedding model ready")
except Exception as e:
    print(f"⚠️  Error loading embedding model: {e}")
    EMBEDDING_READY = False

# Load dataset
print("📂 Loading dataset...")
try:
    if not load_dataset():
        print("⚠️  Warning: Dataset not loaded.")
        DATASET_READY = False
    else:
        DATASET_READY = True
        dataset = get_dataset()
        print(f"✅ Dataset loaded: {len(dataset)} claims")
except Exception as e:
    print(f"⚠️  Error loading dataset: {e}")
    DATASET_READY = False
    dataset = []


def simple_nli_mock(premise, hypothesis):
    """
    Simple mock NLI without downloading BART model.
    Uses semantic similarity heuristic instead.
    """
    # Calculate word overlap as entailment indicator
    premise_words = set(premise.lower().split())
    hypothesis_words = set(hypothesis.lower().split())
    
    if not hypothesis_words:
        return {"entailment": 0.0, "contradiction": 0.0, "neutral": 1.0}
    
    overlap = len(premise_words & hypothesis_words) / len(hypothesis_words)
    
    # If high word overlap → entailment, else neutral
    if overlap > 0.5:
        entailment = min(0.9, overlap + 0.2)
        return {
            "entailment": entailment,
            "contradiction": max(0.0, 0.1 - overlap),
            "neutral": 1.0 - entailment
        }
    else:
        return {"entailment": 0.1, "contradiction": 0.1, "neutral": 0.8}


def aggregate_nli_results(similar_results):
    """Aggregate NLI scores with dataset labels to produce final verdict"""
    if not similar_results:
        return {
            "verdict": "UNCERTAIN",
            "confidence": 0.0,
            "reason": "No similar claims found"
        }
    
    # Weight by similarity score
    total_weight = 0
    entailment_score = 0
    contradiction_score = 0
    neutral_score = 0
    
    for result in similar_results:
        weight = result.get("similarity", 0.5)
        label = result.get("label", 0)
        
        # Get mock NLI scores
        nli_scores = simple_nli_mock(result["text"], result.get("hypothesis", ""))
        
        # Aggregate
        if label == 1:  # Dataset says TRUE
            entailment_score += weight * nli_scores["entailment"]
            contradiction_score += weight * nli_scores["contradiction"] * 0.5
        else:  # Dataset says FALSE
            contradiction_score += weight * nli_scores["contradiction"]
            entailment_score += weight * nli_scores["entailment"] * 0.5
        
        neutral_score += weight * nli_scores["neutral"]
        total_weight += weight
    
    if total_weight == 0:
        return {"verdict": "UNCERTAIN", "confidence": 0.0}
    
    # Normalize scores
    ent_norm = entailment_score / total_weight
    cont_norm = contradiction_score / total_weight
    neu_norm = neutral_score / total_weight
    
    # Determine verdict
    if ent_norm > 0.6:
        verdict = "VERIFIED"
        confidence = min(0.95, ent_norm)
    elif cont_norm > 0.6:
        verdict = "FALSE"
        confidence = min(0.95, cont_norm)
    else:
        verdict = "UNCERTAIN"
        confidence = max(ent_norm, cont_norm, neu_norm)
    
    return {
        "verdict": verdict,
        "confidence": confidence,
        "scores": {
            "entailment": round(ent_norm, 3),
            "contradiction": round(cont_norm, 3),
            "neutral": round(neu_norm, 3)
        }
    }


class VerificationHandler(BaseHTTPRequestHandler):
    """Handle HTTP requests for claim verification"""
    
    def log_message(self, format, *args):
        """Suppress verbose logging"""
        if "health" not in args[0]:
            sys.stderr.write("[%s] %s\n" % (self.client_address[0], format%args))
    
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
                "version": "0.3.0-optimized",
                "mode": "semantic + mock NLI",
                "embedding_model_ready": EMBEDDING_READY,
                "dataset_ready": DATASET_READY,
                "dataset_size": len(dataset) if DATASET_READY else 0,
                "pipeline_stages": ["semantic_search", "mock_nli", "aggregation"]
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        self.send_response(404)
        self.end_headers()
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == "/analyze_claim":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                data = json.loads(body)
                claim = data.get("text", "").strip()
                
                if not claim:
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Empty claim"}).encode())
                    return
                
                if not DATASET_READY or not EMBEDDING_READY:
                    self.send_response(503)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    response = {"error": "System not ready", "dataset_ready": DATASET_READY, "embedding_ready": EMBEDDING_READY}
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                # Run semantic pipeline
                similar_results, stats = semantic_pipeline(claim, dataset, k=5)
                
                # Aggregate results
                aggregated = aggregate_nli_results(similar_results)
                
                # Format response
                response = {
                    "id": str(uuid.uuid4()),
                    "claim": claim,
                    "verdict": aggregated["verdict"],
                    "confidence": aggregated["confidence"],
                    "explanation": f"Based on {len(similar_results)} similar claims from dataset",
                    "sources": [
                        {"name": f"Dataset Claim {i+1}", "credibility": "high"}
                        for i in range(len(similar_results[:3]))
                    ],
                    "pipeline": {
                        "stage_1_semantic_search": f"{stats.get('similar_count', 0)} matches found",
                        "stage_2_nli_inference": "mock mode (heuristic)",
                        "stage_3_aggregation": "completed"
                    },
                    "evidence": {
                        "similar_claims": len(similar_results),
                        "confidence_score": round(aggregated["confidence"] * 100),
                        "scores": aggregated.get("scores", {})
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(response, indent=2).encode())
                
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                error_response = {"error": str(e), "type": type(e).__name__}
                self.wfile.write(json.dumps(error_response).encode())
        else:
            self.send_response(404)
            self.end_headers()


def run_server(port=8000):
    """Start the HTTP server"""
    server = HTTPServer(("localhost", port), VerificationHandler)
    print(f"✅ Server running on http://localhost:{port}")
    print(f"📍 Endpoints:")
    print(f"   • GET  /health")
    print(f"   • POST /analyze_claim")
    print(f"\n🔄 Processing pipeline:")
    print(f"   1️⃣  Semantic Search (embedding + cosine similarity)")
    print(f"   2️⃣  NLI Scoring (mock heuristic mode)")
    print(f"   3️⃣  Result Aggregation → Final Verdict")
    print(f"\n📊 Mode: Semantic + Mock NLI (fast startup, no BART download)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped")
        server.server_close()

if __name__ == "__main__":
    run_server()
