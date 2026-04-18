"""JSON encoder that handles NumPy types and nested structures"""
import json
import numpy as np

def clean_for_json(obj):
    """Recursively clean object to be JSON serializable"""
    if isinstance(obj, dict):
        return {str(k): clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [clean_for_json(v) for v in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    else:
        return obj

def safe_json_dumps(obj):
    """Safely convert to JSON, handling NumPy types and nested structures"""
    cleaned = clean_for_json(obj)
    return json.dumps(cleaned)
