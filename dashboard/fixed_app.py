import os
import pandas as pd
import numpy as np
from flask import Flask, render_template, jsonify, request
from collections import defaultdict
import json
import re
from datetime import datetime
import sys

# Add parent directory to path to import our AI analyzer
sys.path.append('..')
from fixed_simple_ai_analyzer import FixedSimpleAIAAnalyzer

app = Flask(__name__)

# Constants
SAMPLE_SIZE = 1000  # For performance reasons, we'll limit the number of rows to process

# Cache for storing processed data
cache = {}

# Initialize AI Analyzer with the correct base path
try:
    ai_analyzer = FixedSimpleAIAAnalyzer(base_path="/Users/raphael.moreno/AIA-TH-Analytics")
    print("✅ Fixed AI Analyzer integrated successfully")
except Exception as e:
    print(f"⚠️ AI Analyzer initialization failed: {e}")
    ai_analyzer = None

def load_transcript_data(limit=SAMPLE_SIZE):
    """Load and preprocess transcript data from CSV file"""
    if 'transcript_data' in cache:
        return cache['transcript_data']
    
    try:
        # Use our AI analyzer's data loading method if available
        if ai_analyzer:
            df = ai_analyzer.load_transcript_data(limit=limit)
        else:
            # Fallback - shouldn't happen with fixed analyzer
            return pd.DataFrame()
        
        # Cache the result
        cache['transcript_data'] = df
        return df
    except Exception as e:
        print(f"Error loading transcript data: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

def get_ai_insights():
    """Get AI-powered insights about the conversations"""
    if not ai_analyzer:
        return {"error": "AI Analyzer not available"}
    
    try:
        # Get basic statistics
        stats = ai_analyzer.get_basic_stats()
        
        # Get sample analysis
        df = load_transcript_data(limit=100)
        if df.empty or 'Conversation ID' not in df.columns:
            return {"error": "No conversation data available"}
        
        conversation_lengths = df.groupby('Conversation ID').size()
        suitable_conversations = conversation_lengths[conversation_lengths >= 3].index.tolist()
        
        sample_insights = []
        if suitable_conversations:
            # Analyze first few conversations for dashboard display
            for conv_id in suitable_conversations[:5]:
                try:
                    insight = ai_analyzer.analyze_conversation(conv_id)
                    sample_insights.append({
                        'conversation_id': conv_id,
                        'customer_intent': insight.customer_intent,
                        'sentiment': insight.sentiment,
                        'product_interest': insight.product_interest,
                        'issues_count': len(insight.issues_identified),
                        'resolution_status': insight.resolution_status
                    })
                except Exception as e:
                    print(f"Error analyzing {conv_id}: {e}")
                    continue
        
        return {
            'basic_stats': stats,
            'sample_insights': sample_insights,
            'total_analyzed': len(sample_insights)
        }
    except Exception as e:
        return {"error": f"AI analysis failed: {str(e)}"}

def get_conversation_summary(conversation_id=None):
    """Get summary statistics for conversations"""
    df = load_transcript_data()
    
    if df.empty or 'Conversation ID' not in df.columns:
        return []
    
    if conversation_id:
        df = df[df['Conversation ID'] == conversation_id]
    
    try:
        # Group by conversation with proper error handling
        grouped = df.groupby('Conversation ID')
        
        conversation_stats = []
        for conv_id, group in grouped:
            try:
                total_messages = len(group)
                customer_messages = len(group[group['Message Role'] == 'Customer'])
                agent_messages = total_messages - customer_messages
                
                start_time = group['Created At'].min()
                end_time = group['Created At'].max()
                
                # Calculate duration
                if pd.notna(start_time) and pd.notna(end_time):
                    duration_min = (end_time - start_time).total_seconds() / 60
                else:
                    duration_min = 0
                
                conv_stats = {
                    'Conversation ID': conv_id,
                    'Total Messages': total_messages,
                    'Customer Messages': customer_messages,
                    'Agent Messages': agent_messages,
                    'Start Time': start_time,
                    'End Time': end_time,
                    'Duration (min)': duration_min
                }
                
                # Add AI insights if available
                if ai_analyzer:
                    try:
                        insight = ai_analyzer.analyze_conversation(conv_id)
                        conv_stats.update({
                            'AI_Sentiment': insight.sentiment,
                            'AI_Intent': insight.customer_intent[:50] + "..." if len(insight.customer_intent) > 50 else insight.customer_intent,
                            'AI_Issues_Count': len(insight.issues_identified),
                            'AI_Status': insight.resolution_status
                        })
                    except Exception as e:
                        conv_stats.update({
                            'AI_Sentiment': 'unknown',
                            'AI_Intent': 'Analysis failed',
                            'AI_Issues_Count': 0,
                            'AI_Status': 'unknown'
                        })
                
                conversation_stats.append(conv_stats)
                
            except Exception as e:
                print(f"Error processing conversation {conv_id}: {e}")
                continue
        
        return conversation_stats
        
    except Exception as e:
        print(f"Error in get_conversation_summary: {e}")
        return []

def get_agent_performance():
    """Calculate agent performance metrics with AI insights"""
    df = load_transcript_data()
    
    if df.empty or 'Agent ID' not in df.columns:
        return []
    
    # Get unique agents
    agents = df['Agent ID'].unique()
    
    performance_data = []
    
    for agent_id in agents:
        try:
            agent_data_df = df[df['Agent ID'] == agent_id]
            agent_conversations = agent_data_df['Conversation ID'].unique()
            
            agent_data = {
                "Agent ID": agent_id,
                "Conversations": len(agent_conversations),
                "Messages": len(agent_data_df),
                "AI_Insights": {}
            }
            
            # Get AI insights for this agent's conversations
            if ai_analyzer and len(agent_conversations) > 0:
                sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0, 'unknown': 0}
                resolution_counts = {'resolved': 0, 'partially_resolved': 0, 'unresolved': 0, 'unknown': 0}
                total_issues = 0
                analyzed_count = 0
                
                # Analyze up to 5 conversations per agent for performance
                for conv_id in agent_conversations[:5]:
                    try:
                        insight = ai_analyzer.analyze_conversation(conv_id)
                        sentiment_counts[insight.sentiment] = sentiment_counts.get(insight.sentiment, 0) + 1
                        resolution_counts[insight.resolution_status] = resolution_counts.get(insight.resolution_status, 0) + 1
                        total_issues += len(insight.issues_identified)
                        analyzed_count += 1
                    except Exception as e:
                        sentiment_counts['unknown'] += 1
                        resolution_counts['unknown'] += 1
                
                agent_data["AI_Insights"] = {
                    "sentiment_distribution": sentiment_counts,
                    "resolution_distribution": resolution_counts,
                    "avg_issues_per_conversation": round(total_issues / max(analyzed_count, 1), 1),
                    "satisfaction_score": round((sentiment_counts.get('positive', 0) * 5 + sentiment_counts.get('neutral', 0) * 3 + sentiment_counts.get('negative', 0) * 1) / max(sum(sentiment_counts.values()), 1), 1)
                }
            else:
                # Fallback to sample data
                agent_data["AI_Insights"] = {
                    "sentiment_distribution": {"positive": 0, "negative": 0, "neutral": 0, "unknown": 0},
                    "resolution_distribution": {"resolved": 0, "partially_resolved": 0, "unresolved": 0, "unknown": 0},
                    "avg_issues_per_conversation": 0,
                    "satisfaction_score": 3.0
                }
                
            performance_data.append(agent_data)
            
        except Exception as e:
            print(f"Error processing agent {agent_id}: {e}")
            continue
        
    return performance_data

def calculate_sentiment_trends():
    """Calculate sentiment trends over time"""
    if not ai_analyzer:
        return {"error": "AI Analyzer not available"}
    
    try:
        df = load_transcript_data(limit=200)
        
        if df.empty or 'Conversation ID' not in df.columns:
            return {"error": "No conversation data available"}
        
        # Get unique conversations and their dates
        conversations = df.groupby('Conversation ID')['Created At'].first().reset_index()
        conversations = conversations.sort_values('Created At')
        
        # Analyze sentiment for recent conversations
        sentiment_data = []
        for _, row in conversations.head(20).iterrows():  # Analyze last 20 conversations
            try:
                conv_id = row['Conversation ID']
                insight = ai_analyzer.analyze_conversation(conv_id)
                sentiment_data.append({
                    'date': row['Created At'].strftime('%Y-%m-%d') if pd.notna(row['Created At']) else 'Unknown',
                    'conversation_id': conv_id,
                    'sentiment': insight.sentiment,
                    'issues_count': len(insight.issues_identified)
                })
            except Exception as e:
                continue
        
        # Group by date and count sentiments
        sentiment_by_date = {}
        for item in sentiment_data:
            date = item['date']
            if date not in sentiment_by_date:
                sentiment_by_date[date] = {'positive': 0, 'negative': 0, 'neutral': 0}
            sentiment_by_date[date][item['sentiment']] += 1
        
        return {
            'sentiment_trends': sentiment_by_date,
            'raw_data': sentiment_data
        }
    except Exception as e:
        return {"error": f"Sentiment analysis failed: {str(e)}"}

def get_product_insights():
    """Get product-related insights from conversations"""
    if not ai_analyzer:
        return {"error": "AI Analyzer not available"}
    
    try:
        # Generate product opportunities analysis
        opportunities = ai_analyzer.identify_product_opportunities(limit=50)
        
        return {
            'opportunities_analysis': opportunities,
            'status': 'success'
        }
    except Exception as e:
        return {"error": f"Product analysis failed: {str(e)}"}

# Routes
@app.route('/')
def index():
    """Render the main dashboard page"""
    return render_template('index.html')

@app.route('/agents')
def agents():
    """Render the agents page"""
    return render_template('agents.html')

@app.route('/conversations')
def conversations():
    """Render the conversations page"""
    return render_template('conversations.html')

@app.route('/agent/<agent_id>')
def agent_detail(agent_id):
    """Render the agent detail page"""
    return render_template('agent_detail.html', agent_id=agent_id)

@app.route('/conversation/<conversation_id>')
def conversation_detail(conversation_id):
    """Render the conversation detail page"""
    return render_template('conversation_detail.html', conversation_id=conversation_id)

# API endpoints
@app.route('/api/dashboard-overview')
def api_dashboard_overview():
    """API endpoint for dashboard overview data"""
    try:
        ai_insights = get_ai_insights()
        df = load_transcript_data()
        
        overview = {
            'total_conversations': df['Conversation ID'].nunique() if 'Conversation ID' in df.columns and not df.empty else 0,
            'total_messages': len(df) if not df.empty else 0,
            'unique_agents': df['Agent ID'].nunique() if 'Agent ID' in df.columns and not df.empty else 0,
            'date_range': {
                'from': df['Created At'].min().strftime('%Y-%m-%d') if not df.empty and 'Created At' in df.columns and not df['Created At'].isnull().all() else 'N/A',
                'to': df['Created At'].max().strftime('%Y-%m-%d') if not df.empty and 'Created At' in df.columns and not df['Created At'].isnull().all() else 'N/A'
            },
            'ai_insights': ai_insights
        }
        return jsonify(overview)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/conversations')
def api_conversations():
    """API endpoint for conversation data"""
    try:
        return jsonify(get_conversation_summary())
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/conversation/<conversation_id>')
def api_conversation_detail(conversation_id):
    """API endpoint for individual conversation data with AI analysis"""
    try:
        # Get basic conversation data
        basic_data = get_conversation_summary(conversation_id)
        
        # Get detailed AI analysis
        if ai_analyzer:
            insight = ai_analyzer.analyze_conversation(conversation_id)
            
            # Get actual conversation messages
            df = load_transcript_data()
            messages = df[df['Conversation ID'] == conversation_id].to_dict(orient='records') if 'Conversation ID' in df.columns else []
            
            detailed_analysis = {
                'basic_info': basic_data[0] if basic_data else {},
                'ai_analysis': {
                    'customer_intent': insight.customer_intent,
                    'sentiment': insight.sentiment,
                    'product_interest': insight.product_interest,
                    'issues_identified': insight.issues_identified,
                    'resolution_status': insight.resolution_status,
                    'recommendations': insight.recommendations
                },
                'messages': messages
            }
            return jsonify(detailed_analysis)
        else:
            return jsonify({'basic_info': basic_data[0] if basic_data else {}, 'messages': []})
            
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/agents')
def api_agents():
    """API endpoint for agent performance data"""
    try:
        return jsonify(get_agent_performance())
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/sentiment-trends')
def api_sentiment_trends():
    """API endpoint for sentiment trends"""
    return jsonify(calculate_sentiment_trends())

@app.route('/api/product-insights')
def api_product_insights():
    """API endpoint for product insights"""
    return jsonify(get_product_insights())

@app.route('/api/generate-report')
def api_generate_report():
    """API endpoint to generate AI report"""
    if not ai_analyzer:
        return jsonify({"error": "AI Analyzer not available"})
    
    try:
        # Generate comprehensive report
        filename = f"dashboard_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        result = ai_analyzer.generate_full_report(filename)
        
        return jsonify({
            "status": "success",
            "message": result,
            "filename": filename
        })
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    print("🚀 Starting AIA Analytics Dashboard...")
    print(f"📊 AI Analyzer Status: {'✅ Connected' if ai_analyzer else '❌ Not Available'}")
    app.run(debug=True, host='0.0.0.0', port=5050)
