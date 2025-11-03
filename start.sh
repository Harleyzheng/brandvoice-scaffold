#!/bin/bash

# BrandVoice Studio - Quick Start Script
# This script starts both the backend API and frontend UI

set -e

echo "🎭 BrandVoice Studio - Starting Application"
echo "==========================================="
echo ""

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.11+"
    exit 1
fi

# Check if Node is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 16+"
    exit 1
fi

# Check if backend dependencies are installed
echo "📦 Checking backend dependencies..."
if ! python -c "import fastapi" 2>/dev/null; then
    echo "Installing backend dependencies..."
    pip install -r api/requirements.txt
fi

# Check if frontend dependencies are installed
echo "📦 Checking frontend dependencies..."
if [ ! -d "web/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd web && npm install && cd ..
fi

echo ""
echo "✅ All dependencies ready!"
echo ""
echo "Starting servers..."
echo "- Backend API will run on http://localhost:8000"
echo "- Frontend UI will run on http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

trap cleanup INT TERM

# Start backend in background
echo "🚀 Starting backend..."
python api/server.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend in background
echo "🚀 Starting frontend..."
cd web && npm start &
FRONTEND_PID=$!

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID


