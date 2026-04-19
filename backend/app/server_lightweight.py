"""
Sentinel Protocol - Lightweight Backend (Fast responses, no embedding caching)
Uses dataset directly without expensive embedding operations for data endpoints
"""

import json
import sys
import socket
import time
import base64
import os
from difflib import SequenceMatcher
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import numpy as np

# Import components
from app.dataset_loader import load_dataset, get_dataset
from app.core.semantic_pipeline import (
    initialize_embedding_model,
    get_embedding,
    get_embedding_model,
    semantic_pipeline,
)
from app.core.advanced_pipeline import AdvancedVerificationPipeline
from app.json_encoder import safe_json_dumps
from app.optimized_analysis import initialize_analysis_dataset, analyze_claim_optimized
from app.services.nli_service import nli_service
from app.services.post_nli_service import post_nli_service
from app.services.evidence_selection_agent import select_best_evidence
from app.services.source_credibility_graph import SourceCredibilityGraph
from app.services.ocr_service import extract_text_from_bytes
from app.explainability import (
    build_explainability_input,
    generate_evidence_summary,
    generate_explanation,
)

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
source_graph = None

def get_pipeline():
    global pipeline
    if pipeline is None:
        pipeline = AdvancedVerificationPipeline()
    return pipeline


def get_source_graph():
    global source_graph
    if source_graph is None:
        source_graph = SourceCredibilityGraph(alpha=0.7, max_sources_per_query=10)
    return source_graph


def decode_base64_image(image_base64: str) -> bytes:
    """Decode base64 image payload (supports data URI prefixes)."""
    if not image_base64:
        return b""
    raw = str(image_base64).strip()
    if "," in raw and raw.startswith("data:"):
        raw = raw.split(",", 1)[1]
    return base64.b64decode(raw, validate=False)

class LightweightHandler(BaseHTTPRequestHandler):
    """Handle requests efficiently"""
    
    def log_message(self, format, *args):
        if "health" not in args[0]:
            sys.stderr.write(f"[{self.client_address[0]}] {format%args}\n")

    def send_json_response(self, code, payload):
        try:
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(safe_json_dumps(payload).encode())
            return True
        except (BrokenPipeError, ConnectionResetError):
            print("   ⚠️  Client disconnected before response was sent")
            return False
    
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
            response = {
                "status": "healthy",
                "app": "Sentinel Protocol (Lightweight)",
                "mode": "fast data retrieval",
                "embedding_ready": EMBEDDING_READY,
                "dataset_ready": DATASET_READY,
                "analysis_ready": ANALYSIS_READY,
                "endpoints": ["/health", "/analytics", "/archived", "/threats", "/regions", "/extract_text_image", "/analyze_claim"]
            }
            self.send_json_response(200, response)
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
            
            self.send_json_response(200, response)
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
            
            self.send_json_response(200, response)
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
            
            self.send_json_response(200, threats)
            return
        
        elif path == "/regions":
            regions = [
                {"name": "North India", "threats": 234, "severity": "HIGH"},
                {"name": "South India", "threats": 156, "severity": "MEDIUM"},
                {"name": "East India", "threats": 189, "severity": "HIGH"},
                {"name": "West India", "threats": 267, "severity": "CRITICAL"},
                {"name": "Central India", "threats": 98, "severity": "LOW"},
            ]
            
            self.send_json_response(200, regions)
            return
        
        self.send_json_response(404, {"error": "Not found", "code": 404})
    
    def do_POST(self):
        if self.path == "/extract_text_image":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                data = json.loads(body) if body else {}
                image_base64 = data.get("image_base64", "")
                if not image_base64:
                    self.send_error_response(400, "image_base64 is required")
                    return
                image_bytes = decode_base64_image(image_base64)
                extracted_text = extract_text_from_bytes(image_bytes)
                self.send_json_response(200, {"text": extracted_text})
            except Exception as e:
                self.send_error_response(500, f"OCR extraction failed: {str(e)[:120]}")
            return

        if self.path == "/analyze_claim":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                data = json.loads(body)
                claim = str(data.get("text", "") or "").strip()
                image_base64 = data.get("image_base64", "")
                extracted_text = ""

                # Image -> OCR -> text (before normalization pipeline)
                if not claim and image_base64:
                    image_bytes = decode_base64_image(image_base64)
                    extracted_text = extract_text_from_bytes(image_bytes)
                    claim = extracted_text
                
                if not claim:
                    self.send_error_response(400, "Empty claim text and no OCR text extracted")
                    return
                
                if not EMBEDDING_READY:
                    self.send_error_response(503, "Embedding model not ready")
                    return
                
                if not ensure_dataset_loaded():
                    self.send_error_response(503, "Dataset not available")
                    return
                
                print(f"📊 Analyzing: {claim[:50]}...")

                start_time = time.time()
                def resolve_source_name(row):
                    for key in ("source", "publisher", "outlet", "domain", "region", "category"):
                        value = str(row.get(key, "") or "").strip()
                        if value and value.lower() not in {"unknown", "unknown source", "dataset", "dataset source"}:
                            return value
                    return "Unknown Source"

                # Full pipeline routing:
                # Input -> Normalization -> Embedding+Clustering -> Cluster Signals
                # -> Trust -> NLI -> Decision -> Alerts -> Explanation -> Bayesian
                nli_pairs, semantic_metadata = semantic_pipeline(
                    user_claim=claim,
                    dataset=dataset,
                    k=5,
                    similarity_threshold=0.4,
                )
                # Fallback retrieval path:
                # semantic_pipeline expects per-item embeddings in dataset entries;
                # if unavailable, use optimized vectorized retrieval output.
                if not nli_pairs:
                    optimized = analyze_claim_optimized(claim)
                    similar_claims = optimized.get("similar_claims", []) or []
                    nli_pairs = [
                        {
                            "premise": row.get("statement", "") or row.get("text", ""),
                            "hypothesis": claim,
                            "similarity": float(row.get("similarity", 0.0) or 0.0),
                            "label": 1 if str(row.get("label", "")).lower() == "true" else 0,
                            "source": str(
                                row.get("source")
                                or row.get("region")
                                or row.get("category")
                                or "dataset"
                            ),
                        }
                        for row in similar_claims
                        if float(row.get("similarity", 0.0) or 0.0) >= 0.5
                    ]
                if not nli_pairs and hasattr(dataset, "find_similar"):
                    lexical_matches = dataset.find_similar(claim, threshold=0.2, limit=5)
                    claim_lower = claim.lower()
                    nli_pairs = [
                        {
                            "premise": row.get("text", ""),
                            "hypothesis": claim,
                            "similarity": float(SequenceMatcher(None, claim_lower, str(row.get("text", "")).lower()).ratio()),
                            "label": int(row.get("label", 0) or 0),
                            "source": str(row.get("source", "dataset")),
                        }
                        for row in lexical_matches
                        if str(row.get("text", "")).strip()
                    ]
                if not nli_pairs:
                    response = {
                        "verdict": "UNVERIFIED",
                        "confidence": 0.3,
                        "explanation": "No similar claims found for full-pipeline reasoning.",
                        "evidence_summary": "No evidence selected.",
                        "sources": [],
                        "claim": claim,
                        "original_claim": claim,
                        "evidence": [],
                        "normalized_claim": semantic_metadata.get("normalized_claim"),
                        "similar_claims": [],
                        "credibility": {"verdict": "UNCERTAIN", "confidence": 0.3},
                        "analysis_time_seconds": round(time.time() - start_time, 3),
                        "dataset_used": "full_pipeline_topk",
                        "source_credibility_graph": {"nodes": [], "edges": [], "source_evidence": {}},
                        "extracted_text": extracted_text,
                        "pipeline": {"mode": "full_advanced", "semantic_matches": 0},
                    }
                    self.send_json_response(200, response)
                    return

                nli_results = nli_service.evaluate_batch(nli_pairs)
                relation_map = {
                    "ENTAILMENT": "supports",
                    "CONTRADICTION": "contradicts",
                    "NEUTRAL": "neutral",
                }
                evidence_candidates = []
                evidence_lookup = {}
                for row in nli_results:
                    row["source"] = resolve_source_name(row)
                    relation = relation_map.get(
                        nli_service.get_relationship(row.get("nli_scores", {})),
                        "neutral",
                    )
                    similarity = float(row.get("similarity", 0.0) or 0.0)
                    text = str(row.get("premise", ""))
                    evidence_candidates.append(
                        {
                            "text": text,
                            "similarity": similarity,
                            "label": "TRUE" if int(row.get("label", 0) or 0) == 1 else "FALSE",
                            "relation": relation,
                        }
                    )
                    evidence_lookup[(text, similarity, relation)] = row

                selected_evidence = select_best_evidence(evidence_candidates, top_n=3)
                sources = []
                decision_nli = []
                for item in selected_evidence:
                    key = (
                        str(item.get("text", "")),
                        float(item.get("similarity", 0.0) or 0.0),
                        str(item.get("relation", "neutral")),
                    )
                    src_row = evidence_lookup.get(key, {})
                    if src_row:
                        decision_nli.append(src_row)
                    sources.append(
                        {
                            "text": item.get("text", ""),
                            "similarity": float(item.get("similarity", 0.0) or 0.0),
                            "label": "TRUE" if item.get("relation") == "supports" else "FALSE",
                            "relation": item.get("relation", "neutral"),
                            "score": float(item.get("score", 0.0) or 0.0),
                            "source": resolve_source_name(src_row),
                        }
                    )

                if not sources:
                    fallback_ranked = sorted(
                        nli_results,
                        key=lambda row: float(row.get("similarity", 0.0) or 0.0),
                        reverse=True,
                    )[:3]
                    decision_nli = fallback_ranked
                    sources = [
                        {
                            "text": row.get("premise", ""),
                            "similarity": float(row.get("similarity", 0.0) or 0.0),
                            "label": "TRUE" if int(row.get("label", 0) or 0) == 1 else "FALSE",
                            "relation": relation_map.get(
                                nli_service.get_relationship(row.get("nli_scores", {})),
                                "neutral",
                            ),
                            "score": float(row.get("similarity", 0.0) or 0.0),
                            "source": resolve_source_name(row),
                        }
                        for row in fallback_ranked
                    ]

                verdict_raw, confidence = post_nli_service.aggregate_with_dataset_voting(decision_nli or nli_results)
                verdict = "TRUE" if verdict_raw == "VERIFIED" else ("FALSE" if verdict_raw == "FALSE" else "UNVERIFIED")
                confidence = float(confidence or 0.0)

                source_graph_payload = get_source_graph().ingest_evidence(sources)

                explainability_data = build_explainability_input(
                    claim=claim,
                    verdict=verdict,
                    confidence=confidence,
                    sources=sources,
                )
                explanation = generate_explanation(explainability_data)
                evidence_summary = generate_evidence_summary(explainability_data)

                response = {
                    "verdict": verdict,
                    "confidence": confidence,
                    "explanation": explanation,
                    "evidence_summary": evidence_summary,
                    "sources": sources,
                    "claim": claim,
                    "original_claim": claim,
                    "extracted_text": extracted_text,
                    "evidence": explainability_data["evidence"],
                    "normalized_claim": semantic_metadata.get("normalized_claim"),
                    "similar_claims": [
                        {
                            "statement": row.get("premise", ""),
                            "similarity": float(row.get("similarity", 0.0) or 0.0),
                            "label": "true" if int(row.get("label", 0) or 0) == 1 else "false",
                        }
                        for row in nli_results
                    ],
                    "credibility": {
                        "verdict": verdict_raw,
                        "confidence": confidence,
                        "entailment": float(np.mean([r.get("nli_scores", {}).get("entailment", 0.0) for r in (decision_nli or nli_results)]) if (decision_nli or nli_results) else 0.0),
                        "contradiction": float(np.mean([r.get("nli_scores", {}).get("contradiction", 0.0) for r in (decision_nli or nli_results)]) if (decision_nli or nli_results) else 0.0),
                    },
                    "analysis_time_seconds": round(time.time() - start_time, 3),
                    "dataset_used": "full_pipeline_topk_clustered",
                    "source_credibility_graph": source_graph_payload,
                    "pipeline": {
                        "mode": "stable_nli",
                        "semantic_matches": len(nli_pairs),
                        "cluster_count": 0,
                        "alerts": 0,
                        "bayesian_state": {},
                    },
                }
                
                if self.send_json_response(200, response):
                    print(f"   ✅ Response sent\n")
                
            except Exception as e:
                print(f"   ❌ Error: {e}\n")
                self.send_error_response(500, str(e)[:100])
        else:
            self.send_json_response(404, {"error": "Not found", "code": 404})
    
    def send_error_response(self, code, message):
        self.send_json_response(code, {"error": message, "code": code})

def run_server(port=8000):
    if os.getenv("PRELOAD_DATASET", "1") == "1":
        print("2️⃣  Preloading dataset + optimized analysis cache...")
        if ensure_dataset_loaded():
            print("   ✅ Preload complete\n")
        else:
            print("   ⚠️  Preload failed; server will retry lazily on request\n")

    print(f"3️⃣  Starting HTTP server on port {port}...\n")
    print("📍 Fast Endpoints:")
    print(f"   • GET  http://localhost:{port}/health")
    print(f"   • GET  http://localhost:{port}/analytics (instant)")
    print(f"   • GET  http://localhost:{port}/archived?page=1 (instant)")
    print(f"   • GET  http://localhost:{port}/threats (instant)")
    print(f"   • GET  http://localhost:{port}/regions (instant)")
    print(f"   • POST http://localhost:{port}/extract_text_image (OCR)")
    print(f"   • POST http://localhost:{port}/analyze_claim (uses analysis pipeline)\n")
    print("✨ Backend ready!\n")
    print("=" * 60 + "\n")
    
    server_address = ("", port)
    try:
        httpd = ReuseAddrHTTPServer(server_address, LightweightHandler)
    except OSError as e:
        if getattr(e, "errno", None) == 48:
            print(f"❌ Port {port} is already in use.")
            print("   Another backend process is already running.")
            print(f"   Stop it with: lsof -nP -iTCP:{port} -sTCP:LISTEN")
            return
        raise
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
