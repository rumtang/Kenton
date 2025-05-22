#!/bin/bash

# Start both backend and frontend for the Deep Research Agent

echo "Starting Deep Research Agent..."

# Start backend
echo "Starting backend..."
cd "$(dirname "$0")"  # Change to script directory
nohup poetry run python streamlined_api_server.py > backend_raw.log 2>&1 &
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)"

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
sleep 5

# Start frontend
echo "Starting frontend..."
cd "$(dirname "$0")"/frontend
nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend started (PID: $FRONTEND_PID)"

echo "Deep Research Agent is running!"
echo "Backend: http://localhost:8001"
echo "Frontend: http://localhost:3000"
echo ""
echo "To stop: ./stop_all.sh"

# Verify the services started properly
echo ""
echo "Verifying services..."
sleep 3
if ps -p $BACKEND_PID > /dev/null; then
    echo "✅ Backend service is running (PID: $BACKEND_PID)"
else
    echo "❌ Backend service failed to start. Check backend_raw.log for details."
fi

if ps -p $FRONTEND_PID > /dev/null; then
    echo "✅ Frontend service is running (PID: $FRONTEND_PID)"
else
    echo "❌ Frontend service failed to start. Check frontend.log for details."
fi