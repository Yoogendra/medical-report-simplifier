#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Medical Report Simplifier Setup ===${NC}"

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "Python3 could not be found. Please install Python3."
    exit 1
fi

# 1. Setup Virtual Environment
if [ ! -d "venv" ]; then
    echo -e "${GREEN}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

# 2. Install Dependencies
echo -e "${GREEN}Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# 3. Check for .env file
if [ ! -f ".env" ]; then
    echo -e "${BLUE}Creating .env file from .env.example...${NC}"
    cp .env.example .env
    echo "Please update the .env file with your GOOGLE_API_KEY before running."
    exit 1
fi

# 4. Start Services
echo -e "${GREEN}Starting Backend & Frontend...${NC}"

# Stop background processes on script exit
trap 'kill $(jobs -p) 2>/dev/null' EXIT

# Run backend (Flask) in background
cd backend
export FLASK_ENV=development
python app.py &
BACKEND_PID=$!

# Run frontend (Streamlit)
cd ../frontend
streamlit run app.py

# Wait for background processes to finish
wait $BACKEND_PID
