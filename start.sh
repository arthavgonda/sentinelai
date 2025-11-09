#!/bin/bash

echo "Starting OSINT System..."

if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Skipping Docker services..."
    echo "Note: The system will use SQLite instead of PostgreSQL"
else
    echo "Starting PostgreSQL and Redis..."
    # Try docker compose (newer version) first, then docker-compose (older version)
    if command -v docker &> /dev/null && docker compose version &> /dev/null 2>&1; then
        docker compose up -d
    elif command -v docker-compose &> /dev/null; then
        docker-compose up -d
    else
        echo "Docker Compose not found. Skipping Docker services..."
    fi
fi

echo "Waiting for services to be ready..."
sleep 5

echo "Installing backend dependencies..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "Starting backend server..."
python main.py &
BACKEND_PID=$!

cd ../frontend
echo "Installing frontend dependencies..."
npm install

echo "Starting frontend server..."
npm run dev &
FRONTEND_PID=$!

echo "Backend running on http://localhost:8000"
echo "Frontend running on http://localhost:3000"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"

wait

