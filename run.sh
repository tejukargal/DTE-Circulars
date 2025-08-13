#!/bin/bash

echo "Setting up Virtual Environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing/updating dependencies..."
pip install -r requirements.txt

echo ""
echo "Starting DTE Circulars Web App..."
echo "Open your browser and go to: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

python app.py