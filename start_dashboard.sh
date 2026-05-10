#!/bin/bash

# Start the GPU Compute Marketplace Dashboard

echo "🚀 Starting GPU Compute Marketplace Dashboard..."
echo ""
echo "Dashboard will be available at: http://localhost:8000/dashboard.html"
echo "Press Ctrl+C to stop the server"
echo ""

cd "$(dirname "$0")/ui"
python3 -m http.server 8000








