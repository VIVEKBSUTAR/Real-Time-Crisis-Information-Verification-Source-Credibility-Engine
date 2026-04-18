"""Entry point for backend server"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.server_optimized_cache import run_server

if __name__ == "__main__":
    run_server()
