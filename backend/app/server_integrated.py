"""
Sentinel Protocol Backend - Fully Integrated Semantic Pipeline

Complete end-to-end claim verification pipeline:
1. Semantic Processing (normalize → embed → similarity search)
2. NLI Inference (entailment/contradiction detection)
3. Post-NLI Aggregation (verdict generation)

Dataset: 26,232 claims from Bharat Fake News Dataset
"""

import json
import uuid
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Import pipeline components
from app.dataset_loader import load_dataset, get_dataset
from app.core.semantic_pipeline import semantic_pipeline, initialize_embedding_model
from app.services.nli_service import nli_service
from app.services.post_nli_service import post_nli_service

# Initialize models on startup
print("🚀 Initializing Sentinel Protocol Backend...")

# Load embedding model
print("📊 Loading embedding model...")
initialize_embedding_model("all-MiniLM-L6-v2")

# Load dataset
print("📂 Loading dataset...")
if not load_dataset():
    print("⚠️  Warning: Dataset not loaded. System in limited mode.")
    DATASET_READY = False
else:
    DATASET_READY = True
    dataset = get_dataset()
    print(f"✅ Dataset loaded: {len(dataset)} claims")


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
            
            health_response = {
                "status": "healthy",
                "app": "Sentinel Protocol",
                "version": "0.2.0-integrated",
                "message": "Semantic pipeline fully operational",
                "dataset_loaded": DATASET_READY,
                "pipeline": {
                    "semantic_processing": True,
                    "nli_inference": True,
                    "post_nli_aggregation": True
                },
                "dataset_info": {
                    "total_claims": len(get_dataset()) if DATASET_READY else 0,
                    "source": "Bharat Fake News Dataset"
                }
            }
            self.wfile.write(json.dumps(health_response).encode())
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == "/analyze_claim":
            try:
                # Read request
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                request = json.loads(body.decode())
                
                user_claim = request.get('text', '').strip()
                if not user_claim:
                    raise ValueError("Claim text is required")
                
                # Generate claim ID
                claim_id = str(uuid.uuid4())[:8]
                
                # ================================================================
                # STEP 1-6: SEMANTIC PROCESSING PIPELINE
                # ================================================================
                print(f"\n🔍 Analyzing claim: {user_claim[:60]}...")
                
                nli_pairs, semantic_metadata = semantic_pipeline(
                    user_claim=user_claim,
                    dataset=dataset if DATASET_READY else [],
                    k=5,
                    similarity_threshold=0.4
                )
                
                print(f"   ✅ Semantic search found {len(nli_pairs)} matches")
                
                # ================================================================
                # STEP 2: NLI INFERENCE
                # ================================================================
                if not nli_pairs:
                    print("   ⚠️  No similar claims found")
                    response = {
                        "claim_id": claim_id,
                        "original_claim": user_claim,
                        "verdict": "UNCERTAIN",
                        "confidence": 0.3,
                        "explanation": "No similar claims found in dataset for verification.",
                        "evidence": []
                    }
                else:
                    # Run NLI on all pairs
                    print(f"   🧠 Running NLI inference on {len(nli_pairs)} pairs...")
                    nli_results = nli_service.evaluate_batch(nli_pairs)
                    
                    # ================================================================
                    # STEP 3: POST-NLI AGGREGATION
                    # ================================================================
                    print("   📊 Aggregating results...")
                    verdict, confidence = post_nli_service.aggregate_with_dataset_voting(
                        nli_results
                    )
                    
                    # Generate explanation
                    explanation = post_nli_service.format_explanation(
                        user_claim,
                        nli_results,
                        verdict,
                        confidence
                    )
                    
                    # Extract evidence
                    evidence = [
                        {
                            "source": result.get("premise", "")[:100],
                            "similarity": result.get("similarity", 0.0),
                            "label": str(result.get("label", "Unknown")),
                            "nli_entailment": result.get("nli_scores", {}).get("entailment", 0.0)
                        }
                        for result in nli_results[:3]
                    ]
                    
                    response = {
                        "claim_id": claim_id,
                        "original_claim": user_claim,
                        "verdict": verdict,
                        "confidence": float(confidence),
                        "explanation": explanation,
                        "evidence": evidence,
                        "pipeline_stats": {
                            "semantic_matches": len(nli_pairs),
                            "top_similarity": semantic_metadata.get("top_similarity"),
                            "normalized_claim": semantic_metadata.get("normalized_claim")
                        }
                    }
                
                print(f"   ✅ Verdict: {response['verdict']} ({int(response['confidence']*100)}%)\n")
                
                # Send response
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": str(e),
                    "status": "error"
                }).encode())
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())


def run_server(host='0.0.0.0', port=8000):
    """Run the HTTP server"""
    server = HTTPServer((host, port), VerificationHandler)
    print(f"\n✅ Sentinel Protocol Backend listening on {host}:{port}")
    print("   Health: http://localhost:8000/health")
    print("   Analysis: POST http://localhost:8000/analyze_claim")
    print("   Pipeline: Semantic → NLI → Post-NLI")
    print("=" * 70)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        server.shutdown()


if __name__ == '__main__':
    run_server()
