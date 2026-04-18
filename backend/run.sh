#!/bin/bash
set -e

echo "🚀 Starting Sentinel Protocol Backend"
echo "===================================="

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt 2>/dev/null || echo "⚠️  Some packages may not have installed (this is OK for development)"

# Run migrations
echo "🗄️  Setting up database..."
python -m alembic upgrade head 2>/dev/null || echo "⚠️  Alembic not configured yet"

# Start server
echo ""
echo "✅ Backend ready!"
echo ""
echo "🔗 API: http://localhost:8000"
echo "📚 Docs: http://localhost:8000/docs"
echo "🧪 ReDoc: http://localhost:8000/redoc"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
