#!/usr/bin/env python3
"""
Pre-compute and cache embeddings for all dataset claims
Run this once to speed up all future requests 10x
"""
import sys
import os
import time
import pickle
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.semantic_pipeline import initialize_embedding_model, get_embedding
from app.dataset_loader import get_dataset, load_dataset

def cache_embeddings():
    """Generate and cache embeddings for all claims"""
    
    print("\n" + "="*70)
    print("🚀 EMBEDDING CACHE GENERATOR")
    print("="*70 + "\n")
    
    # Step 1: Initialize embedding model
    print("1️⃣  Initializing embedding model...")
    try:
        initialize_embedding_model("all-MiniLM-L6-v2")
        print("   ✅ Model ready\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
        return False
    
    # Step 2: Load dataset
    print("2️⃣  Loading dataset...")
    try:
        if not load_dataset():
            print("   ❌ Failed to load dataset\n")
            return False
        dataset = get_dataset()
        print(f"   ✅ Loaded {len(dataset)} claims\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
        return False
    
    # Step 3: Generate embeddings
    print("3️⃣  Generating embeddings for all claims...")
    print("   ⏳ This takes 5-10 minutes on first run (one-time only)\n")
    
    start_time = time.time()
    embeddings_dict = {}
    
    try:
        for i, claim in enumerate(dataset):
            claim_text = claim.get("text", "")
            claim_id = claim.get("id", f"CLAIM_{i}")
            
            if claim_text.strip():
                try:
                    embedding = get_embedding(claim_text)
                    embeddings_dict[claim_id] = {
                        "text": claim_text,
                        "embedding": embedding.tolist(),  # Convert numpy to list
                        "label": claim.get("label"),
                        "source": claim.get("source", "Unknown")
                    }
                except Exception as e:
                    print(f"   ⚠️  Skipped claim {i}: {str(e)[:50]}")
                    continue
            
            # Progress every 2000 claims
            if (i + 1) % 2000 == 0:
                elapsed = time.time() - start_time
                rate = (i + 1) / elapsed
                remaining = (len(dataset) - i - 1) / rate if rate > 0 else 0
                print(f"   ✓ Processed {i+1:,}/{len(dataset):,} claims | "
                      f"Time: {elapsed:.0f}s | ETA: {remaining:.0f}s")
        
        elapsed = time.time() - start_time
        print(f"\n   ✅ Generated {len(embeddings_dict):,} embeddings in {elapsed:.0f}s\n")
        
    except KeyboardInterrupt:
        print("\n   ⚠️  Interrupted by user\n")
        return False
    except Exception as e:
        print(f"   ❌ Error during generation: {e}\n")
        return False
    
    # Step 4: Save to cache file
    print("4️⃣  Saving to cache file...")
    cache_file = os.path.join(
        os.path.dirname(__file__),
        "embeddings_cache.pkl"
    )
    
    try:
        with open(cache_file, "wb") as f:
            pickle.dump(embeddings_dict, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        file_size_mb = os.path.getsize(cache_file) / (1024 * 1024)
        print(f"   ✅ Saved to: {cache_file}")
        print(f"   📊 Cache size: {file_size_mb:.1f}MB\n")
        
    except Exception as e:
        print(f"   ❌ Error saving cache: {e}\n")
        return False
    
    # Step 5: Verify cache
    print("5️⃣  Verifying cache...")
    try:
        with open(cache_file, "rb") as f:
            loaded = pickle.load(f)
        
        if len(loaded) == len(embeddings_dict):
            print(f"   ✅ Cache verified: {len(loaded):,} embeddings readable\n")
        else:
            print(f"   ❌ Cache mismatch: saved {len(embeddings_dict)}, loaded {len(loaded)}\n")
            return False
            
    except Exception as e:
        print(f"   ❌ Error reading cache: {e}\n")
        return False
    
    # Summary
    print("="*70)
    print("✨ CACHING COMPLETE!")
    print("="*70)
    print(f"\n📊 Summary:")
    print(f"   • Claims processed: {len(embeddings_dict):,}")
    print(f"   • Cache file: {cache_file}")
    print(f"   • Cache size: {file_size_mb:.1f}MB")
    print(f"   • Time taken: {elapsed:.0f}s ({elapsed/60:.1f}m)")
    print(f"\n🚀 Next: Restart backend - it will load from cache!")
    print(f"   Response time: 5-10 seconds (instead of 5-10 minutes)\n")
    
    return True

if __name__ == "__main__":
    success = cache_embeddings()
    sys.exit(0 if success else 1)
