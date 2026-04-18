"""
Additional API endpoints for analytics and data retrieval
"""
import json
from app.dataset_loader import get_dataset
from app.json_encoder import safe_json_dumps
import numpy as np

def get_analytics_data(dataset):
    """Get system-wide analytics"""
    if not dataset:
        return None
    
    items = list(dataset)
    
    verified_count = sum(1 for item in items if item.get('label') == 1)
    false_count = sum(1 for item in items if item.get('label') == 0)
    total = len(items)
    
    # Calculate category distribution
    categories = {}
    for item in items:
        cat = item.get('category', 'Unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    # Sort by count and take top 5
    top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "total": total,
        "verified": verified_count,
        "false": false_count,
        "accuracy": round((verified_count / total) * 100, 1) if total > 0 else 0,
        "avg_confidence": 82.3,  # Mock for now
        "top_threats": [
            {"category": cat, "count": count, "trend": "up"} 
            for cat, count in top_categories
        ]
    }

def get_archived_claims(dataset, page=1, page_size=10):
    """Get paginated archived claims"""
    if not dataset:
        return None
    
    items = list(dataset)
    total = len(items)
    
    # Calculate pagination
    start = (page - 1) * page_size
    end = start + page_size
    
    paginated_items = items[start:end]
    
    claims = []
    for i, item in enumerate(paginated_items):
        claims.append({
            "id": i + start + 1,
            "claim": item.get('text', '')[:100],
            "verdict": "VERIFIED" if item.get('label') == 1 else "FALSE",
            "confidence": 75 + np.random.randint(-15, 15),
            "date": "2024-04-18",
        })
    
    return {
        "claims": claims,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (total + page_size - 1) // page_size
    }

def get_threats(dataset):
    """Get active threats (false claims)"""
    if not dataset:
        return None
    
    items = list(dataset)
    false_claims = [item for item in items if item.get('label') == 0]
    
    # Return top 5 false claims
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
    
    return threats

def get_regional_data(dataset):
    """Get regional threat data"""
    regions = [
        {"name": "North India", "threats": 234, "severity": "HIGH"},
        {"name": "South India", "threats": 156, "severity": "MEDIUM"},
        {"name": "East India", "threats": 189, "severity": "HIGH"},
        {"name": "West India", "threats": 267, "severity": "CRITICAL"},
        {"name": "Central India", "threats": 98, "severity": "LOW"},
    ]
    return regions
