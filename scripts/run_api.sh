#!/bin/bash

# Loan Approval System API Startup Script

set -e

echo "=========================================="
echo "Loan Approval System - API Startup"
echo "=========================================="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -q fastapi==0.104.1 uvicorn==0.24.0 pydantic==2.5.0 pydantic-settings==2.1.0 requests
fi

echo ""
echo "✅ Environment ready!"
echo ""

# Display startup information
echo "=========================================="
echo "Starting FastAPI Server"
echo "=========================================="
echo ""
echo "API Endpoints:"
echo "  - API Base:        http://localhost:8000"
echo "  - Health Check:    http://localhost:8000/health"
echo "  - Swagger Docs:    http://localhost:8000/api/docs"
echo "  - ReDoc:           http://localhost:8000/api/redoc"
echo "  - OpenAPI Schema:  http://localhost:8000/api/openapi.json"
echo ""
echo "Quick Test:"
echo "  Run: python test_api.py (in another terminal)"
echo ""
echo "Documentation:"
echo "  See: API_DOCUMENTATION.md"
echo "  See: README_API.md"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="
echo ""

# Start the API server
python api.py
