#!/bin/bash

# AIA Analytics Dashboard Startup Script
# This script starts your AIA Analytics dashboard with lazy loading

echo "🚀 Starting AIA Analytics Dashboard..."
echo "============================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DASHBOARD_DIR="$DIR/dashboard"
PORT=5801

# Check if we're in the right directory
if [ ! -f "$DASHBOARD_DIR/app.py" ]; then
    echo -e "${RED}❌ Error: Cannot find app.py in $DASHBOARD_DIR${NC}"
    echo "Please run this script from the AIA-TH-Analytics directory"
    exit 1
fi

# Check if log file exists
if [ ! -f "$DIR/log/transcript.csv" ]; then
    echo -e "${YELLOW}⚠️  Warning: No transcript.csv found in log/ directory${NC}"
    echo "The dashboard will start but won't have conversation data"
fi

# Check if .env exists
if [ ! -f "$DIR/.env" ]; then
    echo -e "${YELLOW}⚠️  Warning: No .env file found${NC}"
    echo "AI analysis features may not work without OPENAI_API_KEY"
fi

# AGGRESSIVE PORT KILLER - Kill anything on port 5801
echo -e "${BLUE}🔪 Aggressive port cleanup for port $PORT...${NC}"
echo "Killing any processes using port $PORT..."

# Method 1: Kill by port using lsof
if lsof -i :$PORT >/dev/null 2>&1; then
    echo -e "${YELLOW}Found processes on port $PORT, terminating...${NC}"
    lsof -ti :$PORT | xargs kill -9 2>/dev/null || true
    sleep 1
fi

# Method 2: Kill by process name patterns
echo "Killing Python processes that might be using the port..."
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "flask.*run" 2>/dev/null || true
pkill -f "python.*5801" 2>/dev/null || true

# Method 3: Kill any remaining Flask processes
pgrep -f flask | xargs kill -9 2>/dev/null || true

# Method 4: Extra aggressive - kill any python process in this directory
pgrep -f "$DASHBOARD_DIR" | xargs kill -9 2>/dev/null || true

# Wait a bit for processes to die
sleep 2

# Final check
if lsof -i :$PORT >/dev/null 2>&1; then
    echo -e "${RED}⚠️  Warning: Port $PORT still appears to be in use${NC}"
    echo "Attempting final cleanup..."
    lsof -ti :$PORT | xargs kill -9 2>/dev/null || true
    sleep 2
else
    echo -e "${GREEN}✅ Port $PORT is now free${NC}"
fi

# Change to dashboard directory
cd "$DASHBOARD_DIR"

# Check Python and install requirements if needed
echo -e "${BLUE}🐍 Checking Python environment...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: python3 not found${NC}"
    exit 1
fi

# Install requirements if needed
if [ -f "requirements.txt" ]; then
    echo -e "${BLUE}📦 Installing/updating Python packages...${NC}"
    python3 -m pip install -r requirements.txt --quiet
fi

# Start the dashboard
echo -e "${GREEN}🎯 Starting AIA Analytics Dashboard...${NC}"
echo -e "${BLUE}📊 Features enabled:${NC}"
echo "   • Lazy Loading (10 conversations per page)"
echo "   • On-demand AI Analysis"
echo "   • Real-time Dashboard"
echo "   • Pagination & Search"
echo ""
echo -e "${GREEN}🌐 Dashboard will be available at:${NC}"
echo "   • Main Dashboard: http://localhost:$PORT/"
echo "   • Conversations:  http://localhost:$PORT/conversations"
echo ""
echo -e "${YELLOW}💡 Tips:${NC}"
echo "   • Press Ctrl+C to stop the dashboard"
echo "   • Use 'Click to analyze' for AI insights on conversations"
echo "   • Dashboard loads instantly, conversations load as needed"
echo "   • Port $PORT has been aggressively cleaned before startup"
echo ""
echo -e "${BLUE}🏃 Starting server...${NC}"
echo "============================================"

# Final port check before starting
if lsof -i :$PORT >/dev/null 2>&1; then
    echo -e "${RED}❌ CRITICAL: Port $PORT is STILL in use!${NC}"
    echo "Manual intervention required. Try:"
    echo "sudo lsof -i :$PORT"
    echo "sudo kill -9 <PID>"
    exit 1
fi

# Start the Python application
python3 app.py

# If we get here, the app has stopped
echo ""
echo -e "${YELLOW}⚠️  Dashboard stopped${NC}"
