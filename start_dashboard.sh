#!/bin/bash
# Quick start script for POS Billing Dashboard

echo "======================================"
echo "POS Billing Dashboard"
echo "======================================"
echo ""

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  Flask not installed. Installing dependencies..."
    pip3 install -r requirements.txt
    echo ""
fi

echo "🚀 Starting dashboard..."
echo ""
echo "Dashboard will be available at:"
echo "  → http://localhost:5000"
echo "  → http://$(ipconfig getifaddr en0 2>/dev/null || hostname -I | awk '{print $1}'):5000 (from other devices)"
echo ""
echo "Press Ctrl+C to stop the dashboard"
echo "======================================"
echo ""

python3 dashboard.py
