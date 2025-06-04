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

def analyze_agent_performance(conversation_text, conversation_id):
    """Analyze agent performance based on conversation content"""
    
    # Extract agent responses for analysis
    lines = conversation_text.split('\n')
    agent_responses = [line.split(': ', 1)[1] for line in lines if line.startswith('Agent: ')]
    customer_prompts = [line.split(': ', 1)[1] for line in lines if line.startswith('Customer: ')]
    
    # Initialize performance metrics
    performance = {
        'product_pitch': {
            'explain_benefits': {'score': 0, 'explanation': 'Not demonstrated'},
            'explain_details': {'score': 0, 'explanation': 'Not demonstrated'},  
            'answer_questions': {'score': 0, 'explanation': 'Not demonstrated'},
            'close_conversation': {'score': 0, 'explanation': 'Not demonstrated'}
        },
        'objection_handling': {
            'listening': {'score': 0, 'explanation': 'Not demonstrated'},
            'acknowledging': {'score': 0, 'explanation': 'Not demonstrated'},
            'defusing': {'score': 0, 'explanation': 'Not demonstrated'},
            'refocusing': {'score': 0, 'explanation': 'Not demonstrated'}
        },
        'communication_skills': {
            'small_talk': {'score': 0, 'explanation': 'Not demonstrated'},
            'content_organization': {'score': 0, 'explanation': 'Not demonstrated'},
            'building_rapport': {'score': 0, 'explanation': 'Not demonstrated'},
            'relevant_examples': {'score': 0, 'explanation': 'Not demonstrated'},
            'active_listening': {'score': 0, 'explanation': 'Not demonstrated'},
            'closing': {'score': 0, 'explanation': 'Not demonstrated'}
        }
    }
    
    # Analyze communication skills - Small talk
    if any(keyword in ' '.join(agent_responses).lower() for keyword in ['football', 'match', 'arsenal', 'game']):
        performance['communication_skills']['small_talk'] = {
            'score': 4, 
            'explanation': 'Engaged well in football discussion, showed personality'
        }
        performance['communication_skills']['building_rapport'] = {
            'score': 4,
            'explanation': 'Good rapport building through shared interests'
        }
    
    # Check for insurance-related content
    insurance_keywords = ['insurance', 'policy', 'coverage', 'premium', 'benefit', 'life insurance', 'protection']
    insurance_discussion = any(keyword in ' '.join(agent_responses).lower() for keyword in insurance_keywords)
    
    if insurance_discussion:
        performance['product_pitch']['explain_benefits']['score'] = 3
        performance['product_pitch']['explain_benefits']['explanation'] = 'Mentioned insurance products'
        performance['communication_skills']['content_organization']['score'] = 3
        performance['communication_skills']['content_organization']['explanation'] = 'Transitioned to business discussion'
    
    # Analyze response quality
    total_agent_words = sum(len(response.split()) for response in agent_responses)
    avg_response_length = total_agent_words / len(agent_responses) if agent_responses else 0
    
    if avg_response_length > 10:
        performance['communication_skills']['active_listening']['score'] = 3
        performance['communication_skills']['active_listening']['explanation'] = 'Provided detailed responses'
    elif avg_response_length < 3:
        performance['communication_skills']['active_listening']['score'] = 2
        performance['communication_skills']['active_listening']['explanation'] = 'Very brief responses, may indicate disengagement'
    
    # Check for professional language and courtesy
    if any(word in ' '.join(agent_responses).lower() for word in ['please', 'thank', 'appreciate']):
        performance['communication_skills']['building_rapport']['score'] = max(
            performance['communication_skills']['building_rapport']['score'], 3
        )
    
    return performance

def get_session_summary(conversation_id, conversation_data):
    """Generate session summary for dashboard display"""
    
    # Calculate basic metrics
    agent_messages = len(conversation_data[conversation_data['Message Role'] == 'Agent'])
    customer_messages = len(conversation_data[conversation_data['Message Role'] == 'Customer'])
    total_messages = len(conversation_data)
    
    # Analyze conversation content
    conversation_text = ""
    for _, row in conversation_data.iterrows():
        role = row['Message Role']
        text = row['Message Text']
        conversation_text += f"{role}: {text}\n"
    
    # Get AI performance analysis
    performance = analyze_agent_performance(conversation_text, conversation_id)
    
    # Calculate category averages
    product_pitch_avg = np.mean([
        performance['product_pitch']['explain_benefits']['score'],
        performance['product_pitch']['explain_details']['score'],
        performance['product_pitch']['answer_questions']['score'],
        performance['product_pitch']['close_conversation']['score']
    ])
    
    objection_handling_avg = np.mean([
        performance['objection_handling']['listening']['score'],
        performance['objection_handling']['acknowledging']['score'],
        performance['objection_handling']['defusing']['score'],
        performance['objection_handling']['refocusing']['score']
    ])
    
    communication_skills_avg = np.mean([
        performance['communication_skills']['small_talk']['score'],
        performance['communication_skills']['content_organization']['score'],
        performance['communication_skills']['building_rapport']['score'],
        performance['communication_skills']['relevant_examples']['score'],
        performance['communication_skills']['active_listening']['score'],
        performance['communication_skills']['closing']['score']
    ])
    
    overall_score = np.mean([product_pitch_avg, objection_handling_avg, communication_skills_avg])
    
    # Determine strengths and improvement areas
    category_scores = {
        'Product Pitch': product_pitch_avg,
        'Objection Handling': objection_handling_avg,
        'Communication Skills': communication_skills_avg
    }
    
    strengths = [k for k, v in category_scores.items() if v >= 3.5]
    improvement_areas = [k for k, v in category_scores.items() if v < 3.0]
    
    # Determine scenario type based on conversation content
    scenario_type = "General Practice"
    if "insurance" in conversation_text.lower():
        scenario_type = "Product Pitch"
    if any(word in conversation_text.lower() for word in ["objection", "expensive", "costly", "cheap"]):
        scenario_type = "Objection Handling"
    
    # Generate AI feedback
    if overall_score >= 4.0:
        ai_feedback = "Excellent performance! Strong across all areas."
        practice_status = "Completed - Excellent"
    elif overall_score >= 3.0:
        ai_feedback = f"Good foundation. Focus on: {', '.join(improvement_areas) if improvement_areas else 'maintaining consistency'}"
        practice_status = "Completed - Good"
    elif overall_score >= 2.0:
        ai_feedback = f"Needs improvement in: {', '.join(improvement_areas)}. Consider additional practice."
        practice_status = "Needs Review"
    else:
        ai_feedback = "Significant improvement needed. Recommend manager review."
        practice_status = "Requires Attention"
    
    return {
        'session_id': conversation_id,
        'agent_id': conversation_data['Agent ID'].iloc[0] if 'Agent ID' in conversation_data.columns else 'Unknown',
        'practice_date': conversation_data['Created At'].iloc[0] if 'Created At' in conversation_data.columns else None,
        'total_messages': total_messages,
        'agent_messages': agent_messages,
        'customer_messages': customer_messages,
        'scenario_type': scenario_type,
        'performance_score': round(overall_score, 1),
        'product_pitch_score': round(product_pitch_avg, 1),
        'objection_handling_score': round(objection_handling_avg, 1),
        'communication_skills_score': round(communication_skills_avg, 1),
        'strengths': strengths,
        'improvement_areas': improvement_areas,
        'ai_feedback': ai_feedback,
        'practice_status': practice_status,
        'detailed_performance': performance
    }

def load_paginated_sessions(page=1, per_page=ITEMS_PER_PAGE, search=None, performance_filter=None, status_filter=None):
    """Load practice sessions with pagination and filtering"""
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
        
        # Group by conversation to get session data
        session_summaries = []
        unique_conversations = df['Conversation ID'].unique()
        
        for conv_id in unique_conversations:
            conv_data = df[df['Conversation ID'] == conv_id]
            session_summary = get_session_summary(conv_id, conv_data)
            session_summaries.append(session_summary)
        
        # Sort by date (most recent first)
        session_summaries.sort(key=lambda x: x['practice_date'] if pd.notna(x['practice_date']) else datetime.min, reverse=True)
        
        # Apply filters
        if search:
            search_lower = search.lower()
            session_summaries = [
                session for session in session_summaries 
                if search_lower in session['session_id'].lower() or 
                   search_lower in session['agent_id'].lower() or
                   search_lower in session['scenario_type'].lower()
            ]
        
        if performance_filter:
            if performance_filter == 'excellent':
                session_summaries = [s for s in session_summaries if s['performance_score'] >= 4.0]
            elif performance_filter == 'good':
                session_summaries = [s for s in session_summaries if 3.0 <= s['performance_score'] < 4.0]
            elif performance_filter == 'needs_improvement':
                session_summaries = [s for s in session_summaries if s['performance_score'] < 3.0]
        
        if status_filter:
            session_summaries = [
                session for session in session_summaries 
                if session['practice_status'].lower().replace(' ', '_').replace('-', '_') == status_filter.lower()
            ]
        
        # Calculate pagination
        total_items = len(session_summaries)
        total_pages = math.ceil(total_items / per_page)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        paginated_data = session_summaries[start_idx:end_idx]
        
        return {
            'sessions': paginated_data,
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total_items': total_items,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }
        
    except Exception as e:
        print(f"Error loading paginated sessions: {e}")
        return {
            'sessions': [],
            'pagination': {
                'current_page': 1,
                'per_page': per_page,
                'total_items': 0,
                'total_pages': 0,
                'has_next': False,
                'has_prev': False
            }
        }

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sessions')
def sessions():
    return render_template('sessions.html')

@app.route('/conversations')
def conversations():
    return render_template('conversations_lazy.html')

# API endpoints
@app.route('/api/sessions')
def api_sessions():
    """API endpoint for paginated session data"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', ITEMS_PER_PAGE))
        search = request.args.get('search', '').strip()
        performance_filter = request.args.get('performance', '').strip()
        status_filter = request.args.get('status', '').strip()
        
        # Validate parameters
        page = max(1, page)
        per_page = min(50, max(5, per_page))
        
        result = load_paginated_sessions(
            page=page,
            per_page=per_page,
            search=search if search else None,
            performance_filter=performance_filter if performance_filter else None,
            status_filter=status_filter if status_filter else None
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/session/<session_id>/details')
def api_session_details(session_id):
    """API endpoint to get detailed session analysis"""
    try:
        df = pd.read_csv(LOG_FILE_PATH)
        df.columns = df.columns.str.strip()
        df = df[df['Message Role'] != 'N/A']
        df = df[df['Message Text'].notna()]
        
        conv_data = df[df['Conversation ID'] == session_id]
        if conv_data.empty:
            return jsonify({"error": "Session not found"})
        
        session_summary = get_session_summary(session_id, conv_data)
        return jsonify(session_summary)
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/agent-performance-overview')
def api_agent_performance_overview():
    """API endpoint for agent performance overview on dashboard"""
    try:
        # Load and process data
        df = pd.read_csv(LOG_FILE_PATH)
        df.columns = df.columns.str.strip()
        df = df[df['Message Role'] != 'N/A']
        df = df[df['Message Text'].notna()]
        df = df[df['Message Text'] != 'No transcript available']
        
        total_sessions = df['Conversation ID'].nunique()
        unique_agents = df['Agent ID'].nunique() if 'Agent ID' in df.columns else 1
        
        # Quick analysis of few sessions for overview
        sample_sessions = []
        for conv_id in df['Conversation ID'].unique()[:10]:  # Sample first 10
            conv_data = df[df['Conversation ID'] == conv_id]
            session_summary = get_session_summary(conv_id, conv_data)
            sample_sessions.append(session_summary)
        
        if sample_sessions:
            avg_performance = np.mean([s['performance_score'] for s in sample_sessions])
            avg_product_pitch = np.mean([s['product_pitch_score'] for s in sample_sessions])
            avg_objection_handling = np.mean([s['objection_handling_score'] for s in sample_sessions])
            avg_communication = np.mean([s['communication_skills_score'] for s in sample_sessions])
            
            # Count performance levels
            excellent_count = len([s for s in sample_sessions if s['performance_score'] >= 4.0])
            good_count = len([s for s in sample_sessions if 3.0 <= s['performance_score'] < 4.0])
            needs_improvement_count = len([s for s in sample_sessions if s['performance_score'] < 3.0])
        else:
            avg_performance = 0
            avg_product_pitch = avg_objection_handling = avg_communication = 0
            excellent_count = good_count = needs_improvement_count = 0
        
        performance_data = {
            'total_agents': unique_agents,
            'total_sessions': total_sessions,
            'avg_performance': round(avg_performance, 1),
            'sessions_analyzed': len(sample_sessions),
            'has_analysis': len(sample_sessions) > 0,
            'analysis_status': f'Analyzed {len(sample_sessions)} sample sessions. Click "Analyze All Sessions" for complete analysis.',
            'product_pitch': {
                'score': round(avg_product_pitch, 1),
                'status': 'good' if avg_product_pitch >= 3.5 else 'needs-improvement' if avg_product_pitch >= 2.5 else 'poor'
            },
            'objection_handling': {
                'score': round(avg_objection_handling, 1),
                'status': 'good' if avg_objection_handling >= 3.5 else 'needs-improvement' if avg_objection_handling >= 2.5 else 'poor'
            },
            'communication': {
                'score': round(avg_communication, 1),
                'status': 'good' if avg_communication >= 3.5 else 'needs-improvement' if avg_communication >= 2.5 else 'poor'
            },
            'performance_distribution': {
                'excellent': excellent_count,
                'good': good_count,
                'needs_improvement': needs_improvement_count
            },
            'top_performers': [
                {
                    'rank': i+1,
                    'agent_id': session['agent_id'],
                    'session_id': session['session_id'],
                    'overall_score': session['performance_score']
                }
                for i, session in enumerate(sorted(sample_sessions, key=lambda x: x['performance_score'], reverse=True)[:3])
            ],
            'needs_attention': [
                {
                    'agent_id': session['agent_id'],
                    'session_id': session['session_id'],
                    'issue_type': 'low_performance',
                    'weakest_area': session['improvement_areas'][0] if session['improvement_areas'] else 'General',
                    'overall_score': session['performance_score']
                }
                for session in sorted(sample_sessions, key=lambda x: x['performance_score'])[:3]
                if session['performance_score'] < 3.0
            ]
        }
        
        return jsonify(performance_data)
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/training-recommendations')
def api_training_recommendations():
    """API endpoint for training recommendations"""
    try:
        # Load sample data for recommendations
        df = pd.read_csv(LOG_FILE_PATH)
        df.columns = df.columns.str.strip()
        df = df[df['Message Role'] != 'N/A']
        df = df[df['Message Text'].notna()]
        
        sample_sessions = []
        for conv_id in df['Conversation ID'].unique()[:20]:  # Analyze more for recommendations
            conv_data = df[df['Conversation ID'] == conv_id]
            session_summary = get_session_summary(conv_id, conv_data)
            sample_sessions.append(session_summary)
        
        # Analyze common weaknesses
        all_improvement_areas = []
        for session in sample_sessions:
            all_improvement_areas.extend(session['improvement_areas'])
        
        from collections import Counter
        weakness_counts = Counter(all_improvement_areas)
        
        recommendations_list = []
        
        if weakness_counts.get('Objection Handling', 0) > len(sample_sessions) * 0.3:
            recommendations_list.append({
                "title": "Objection Handling Workshop",
                "description": f"{weakness_counts['Objection Handling']} agents need improvement in handling customer objections and concerns",
                "priority": "high",
                "affected_agents": weakness_counts['Objection Handling']
            })
        
        if weakness_counts.get('Product Pitch', 0) > len(sample_sessions) * 0.2:
            recommendations_list.append({
                "title": "Product Knowledge Training",
                "description": f"{weakness_counts['Product Pitch']} agents need better product knowledge and presentation skills",
                "priority": "medium",
                "affected_agents": weakness_counts['Product Pitch']
            })
        
        if weakness_counts.get('Communication Skills', 0) > len(sample_sessions) * 0.2:
            recommendations_list.append({
                "title": "Communication Skills Enhancement",
                "description": f"{weakness_counts['Communication Skills']} agents need improvement in communication and rapport building",
                "priority": "medium",
                "affected_agents": weakness_counts['Communication Skills']
            })
        
        # Add general recommendations if no specific weaknesses found
        if not recommendations_list:
            recommendations_list = [
                {
                    "title": "Advanced Sales Techniques",
                    "description": "Continue building on strong foundation with advanced sales methodologies",
                    "priority": "leverage",
                    "affected_agents": len(sample_sessions)
                },
                {
                    "title": "Role-Play Practice Sessions",
                    "description": "Regular practice sessions to maintain and improve current skill levels",
                    "priority": "medium",
                    "affected_agents": len(sample_sessions)
                }
            ]
        
        recommendations = {
            "total_analyzed": len(sample_sessions),
            "recommendations": recommendations_list
        }
        return jsonify(recommendations)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    print("🚀 Starting AIA Analytics Dashboard - Agent Performance Focus...")
    print(f"📊 AI Analyzer Status: {'✅ Connected' if ai_analyzer else '❌ Not Available'}")
    app.run(debug=True, host='0.0.0.0', port=5801)
