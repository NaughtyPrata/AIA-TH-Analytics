#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install werkzeug==2.0.3
pip install flask==2.0.1
pip install numpy
pip install pandas
pip install gunicorn==20.1.0
pip install python-dateutil==2.8.2

# Run the application
echo "Starting the dashboard..."
python app.py 