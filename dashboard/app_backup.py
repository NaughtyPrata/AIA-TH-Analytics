import os
import pandas as pd
import numpy as np
from flask import Flask, render_template, jsonify, request
from collections import defaultdict
import json
import re
from datetime import datetime
import sys
import math

# Add parent directory to path to import our AI analyzer
sys.path.append('..')
from simple_ai_analyzer import SimpleAIAAnalyzer

app = Flask(__name__)

# Constants
LOG_FILE_PATH = '../log/transcript.csv'
ITEMS_PER_PAGE = 10  # Default items per page for lazy loading

# Cache for storing processed data
cache = {}

# Initialize AI Analyzer
try:
    ai_analyzer = SimpleAIAAnalyzer()
    print("✅ AI Analyzer integrated successfully")
except Exception as e:
    print(f"⚠️ AI Analyzer initialization failed: {e}")
    ai_analyzer = None

def get_total_conversations_count():
    """Get total number of unique conversations without loading all data"""
    try:
        if 'total_conversations' not in cache:
            df = pd.read_csv(LOG_FILE_PATH, usecols=['Conversation ID'])
            df = df[df['Conversation ID'].notna()]
            total_count = df['Conversation ID'].nunique()
            cache['total_conversations'] = total_count
        return cache['total_conversations']
    except Exception as e:
        print(f"Error counting conversations: {e}")
        return 0

def load_paginated_conversations(page=1, per_page=ITEMS_PER_PAGE, search=None, sentiment_filter=None, status_filter=None):
    """Load conversations with pagination and filtering"""
    try:
        # Load full dataset
        df = pd.read_csv(LOG_FILE_PATH)
        df.columns = df.columns.str.strip()
        
        # Clean data
        df = df[df['Message Role'] != 'N/A']
        df = df[df['Message Text'].notna()]
        df = df[df['Message Text'] != 'No transcript available']
        
        # Convert date column
        df['Created At'] = pd.to_datetime(df['Created At'], format='%Y-%m-%d %H:%M:%S (GMT+7)', errors='coerce')
        
        # Group by conversation to get summary stats
        grouped = df.groupby('Conversation ID').agg({
            'Created At': ['min', 'max'],
            'Message Role': 'count',
            'Agent ID': 'first'
        }).reset_index()
        
        # Flatten column names
        grouped.columns = ['Conversation ID', 'Start Time', 'End Time', 'Total Messages', 'Agent ID']
        
        # Calculate duration and message breakdown
        conversation_stats = []
        for _, row in grouped.iterrows():
            conv_id = row['Conversation ID']
            conv_data = df[df['Conversation ID'] == conv_id]
            
            customer_messages = len(conv_data[conv_data['Message Role'] == 'Customer'])
            agent_messages = len(conv_data[conv_data['Message Role'] == 'Agent'])
            
            conv_stats = {
                'Conversation ID': conv_id,
                'Start Time': row['Start Time'],
                'End Time': row['End Time'],
                'Total Messages': row['Total Messages'],
                'Customer Messages': customer_messages,
                'Agent Messages': agent_messages,
                'Agent ID': row['Agent ID'],
                # Placeholder for AI analysis - will