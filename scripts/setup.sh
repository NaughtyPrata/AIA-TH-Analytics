#!/bin/bash

echo "🚀 Setting up AIA Analytics AI Analyzer"
echo "======================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip."
    exit 1
fi

# Install required packages
echo "📦 Installing required packages..."
pip3 install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please ensure you have your OpenAI API key in the .env file."
    exit 1
fi

echo "✅ Setup complete!"
echo ""
echo "🎯 Usage Options:"
echo "1. Interactive Analysis:    python3 ai_analyzer.py"
echo "2. Quick Summary:          python3 quick_analysis.py summary"
echo "3. Analyze Conversation:   python3 quick_analysis.py analyze CONVERSATION_ID"
echo "4. Jupyter Notebook:       jupyter notebook analysis_notebook.ipynb"
echo ""
echo "📊 Ready to analyze your AIA conversation data!"
