#!/bin/bash

# Start both backend and frontend for the Deep Research Agent

echo "Starting Deep Research Agent..."

# Start backend
echo "Starting backend..."
cd "$(dirname "$0")"  # Change to script directory
nohup python streamlined_api_server.py > backend_raw.log 2>&1 &
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)"

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
sleep 3

# Start frontend
echo "Starting frontend..."
cd "$(dirname "$0")"/frontend
npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend started (PID: $FRONTEND_PID)"

echo "Deep Research Agent is running!"
echo "Backend: http://localhost:8001"
echo "Frontend: http://localhost:3000"
echo ""
echo "To stop: ./stop_all.sh"