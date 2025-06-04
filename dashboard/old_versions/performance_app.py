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
from agent_performance_analyzer import AgentPerformanceAnalyzer

app = Flask(__name__)

# Cache for storing processed data and AI analysis results
cache = {
    'performance_data': None,
    'last_analysis_time': None,
    'analysis_results': []
}

# Initialize Agent Performance Analyzer with the correct base path
try:
    performance_analyzer = AgentPerformanceAnalyzer(base_path="/Users/raphael.moreno/AIA-TH-Analytics")
    print("✅ Agent Performance Analyzer integrated successfully")
except Exception as e:
    print(f"⚠️ Agent Performance Analyzer initialization failed: {e}")
    performance_analyzer = None

def get_cached_performance_data():
    """Get cached performance data or load basic stats without AI analysis"""
    if cache['performance_data'] is None:
        if not performance_analyzer:
            return {"error": "Performance Analyzer not available"}
        
        try:
            # Only get basic overview data, no AI analysis yet
            cache['performance_data'] = performance_analyzer.get_agent_performance_overview()
            print("📊 Basic performance data cached")
        except Exception as e:
            return {"error": f"Failed to get overview: {str(e)}"}
    
    return cache['performance_data']

def get_cached_analysis_results():
    """Get cached AI analysis results"""
    return cache['analysis_results']

def refresh_ai_analysis():
    """Refresh AI analysis results - only called when user clicks refresh"""
    if not performance_analyzer:
        return {"error": "Performance Analyzer not available"}
    
    try:
        print("🔄 Refreshing AI analysis...")
        cache['analysis_results'] = performance_analyzer.analyze_multiple_agents(num_conversations=5)
        cache['last_analysis_time'] = datetime.now()
        print(f"✅ AI analysis refreshed - {len(cache['analysis_results'])} conversations analyzed")
        return {"success": True, "analyzed": len(cache['analysis_results'])}
    except Exception as e:
        print(f"❌ Error refreshing AI analysis: {e}")
        return {"error": str(e)}

def get_top_performers(performance_scores):
    """Get top performing agents"""
    if not performance_scores:
        return []
    
    # Sort by overall score
    sorted_scores = sorted(performance_scores, key=lambda x: x.overall_score, reverse=True)
    
    top_performers = []
    for i, score in enumerate(sorted_scores[:3]):
        top_performers.append({
            'rank': i + 1,
            'agent_id': score.agent_id[-8:],  # Show last 8 chars of agent ID
            'conversation_id': score.conversation_id,
            'overall_score': score.overall_score,
            'performance_level': score.performance_level,
            'sessions': 1  # For now, counting each conversation as a session
        })
    
    return top_performers

def get_needs_attention(performance_scores):
    """Get agents that need attention"""
    if not performance_scores:
        return []
    
    # Find agents with low scores or specific issues
    needs_attention = []
    for score in performance_scores:
        if score.overall_score < 3.0 or score.performance_level in ['POOR', 'NEEDS_IMPROVEMENT']:
            # Find the weakest area
            weakest_area = "overall performance"
            weakest_score = score.overall_score
            
            if score.objection_handling_score < score.product_pitch_score and score.objection_handling_score < score.communication_skills_score:
                weakest_area = "objection handling"
                weakest_score = score.objection_handling_score
            elif score.product_pitch_score < score.communication_skills_score:
                weakest_area = "product pitch"
                weakest_score = score.product_pitch_score
            else:
                weakest_area = "communication skills"
                weakest_score = score.communication_skills_score
            
            needs_attention.append({
                'agent_id': score.agent_id[-8:],
                'conversation_id': score.conversation_id,
                'overall_score': score.overall_score,
                'weakest_area': weakest_area,
                'weakest_score': weakest_score,
                'issue_type': 'low_performance' if score.overall_score < 2.5 else 'needs_improvement'
            })
    
    return needs_attention[:3]  # Return top 3 that need attention

def calculate_category_averages(performance_scores):
    """Calculate average scores for each category"""
    if not performance_scores:
        return {
            'product_pitch': 0,
            'objection_handling': 0, 
            'communication_skills': 0
        }
    
    return {
        'product_pitch': sum(s.product_pitch_score for s in performance_scores) / len(performance_scores),
        'objection_handling': sum(s.objection_handling_score for s in performance_scores) / len(performance_scores),
        'communication_skills': sum(s.communication_skills_score for s in performance_scores) / len(performance_scores)
    }

def get_performance_level(score):
    """Get performance level based on score"""
    if score >= 4.5:
        return 'excellent'
    elif score >= 3.5:
        return 'good'
    elif score >= 2.5:
        return 'needs-improvement'
    else:
        return 'poor'

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
@app.route('/api/agent-performance-overview')
def api_agent_performance_overview():
    """API endpoint for agent performance overview data - uses cached data"""
    try:
        # Get basic overview data (no AI analysis)
        overview = get_cached_performance_data()
        
        if "error" in overview:
            return jsonify(overview)
        
        # Get cached AI analysis results
        performance_scores = get_cached_analysis_results()
        
        if performance_scores:
            # Calculate averages from cached analysis
            category_averages = calculate_category_averages(performance_scores)
            overall_avg = sum(category_averages.values()) / 3 if category_averages else 0
            
            # Get insights
            top_performers = get_top_performers(performance_scores)
            needs_attention = get_needs_attention(performance_scores)
            
            analysis_status = f"Last analyzed: {cache['last_analysis_time'].strftime('%H:%M:%S')}" if cache['last_analysis_time'] else "No AI analysis yet"
        else:
            # No AI analysis yet - show basic data only
            category_averages = {'product_pitch': 0, 'objection_handling': 0, 'communication_skills': 0}
            overall_avg = 0
            top_performers = []
            needs_attention = []
            analysis_status = "Click 'Refresh AI Insights' to analyze agent performance"
        
        dashboard_data = {
            'total_agents': overview.get('total_agents', 0),
            'total_sessions': overview.get('total_sessions', 0),
            'avg_performance': round(overall_avg, 1) if overall_avg > 0 else 0,
            'improvement_rate': overview.get('improvement_rate', '+0%'),
            'product_pitch': {
                'score': round(category_averages['product_pitch'], 1),
                'status': get_performance_level(category_averages['product_pitch'])
            },
            'objection_handling': {
                'score': round(category_averages['objection_handling'], 1),
                'status': get_performance_level(category_averages['objection_handling'])
            },
            'communication': {
                'score': round(category_averages['communication_skills'], 1),
                'status': get_performance_level(category_averages['communication_skills'])
            },
            'top_performers': top_performers,
            'needs_attention': needs_attention,
            'total_analyzed': len(performance_scores),
            'analysis_status': analysis_status,
            'has_analysis': len(performance_scores) > 0
        }
        
        return jsonify(dashboard_data)
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/refresh-ai-insights', methods=['POST'])
def api_refresh_ai_insights():
    """API endpoint to refresh AI insights - only called when user clicks button"""
    try:
        result = refresh_ai_analysis()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/analyze-conversation/<conversation_id>')
def api_analyze_conversation(conversation_id):
    """API endpoint for analyzing a specific conversation"""
    if not performance_analyzer:
        return jsonify({"error": "Performance Analyzer not available"})
    
    try:
        score = performance_analyzer.analyze_agent_performance(conversation_id)
        
        return jsonify({
            'conversation_id': score.conversation_id,
            'agent_id': score.agent_id,
            'overall_score': score.overall_score,
            'product_pitch_score': score.product_pitch_score,
            'objection_handling_score': score.objection_handling_score,
            'communication_skills_score': score.communication_skills_score,
            'performance_level': score.performance_level,
            'key_strengths': score.key_strengths,
            'improvement_areas': score.improvement_areas,
            'training_recommendations': score.training_recommendations,
            'detailed_scores': score.detailed_scores
        })
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/generate-performance-report')
def api_generate_performance_report():
    """API endpoint to generate agent performance report"""
    if not performance_analyzer:
        return jsonify({"error": "Performance Analyzer not available"})
    
    try:
        filename = f"agent_performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        result = performance_analyzer.generate_performance_report(filename)
        
        return jsonify({
            "status": "success",
            "message": result,
            "filename": filename
        })
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/training-recommendations')
def api_training_recommendations():
    """API endpoint for AI training recommendations"""
    try:
        # Use cached analysis results
        performance_scores = get_cached_analysis_results()
        
        if not performance_scores:
            return jsonify({"error": "No AI analysis available. Click 'Refresh AI Insights' first."})
        
        # Analyze common patterns
        low_objection_count = sum(1 for s in performance_scores if s.objection_handling_score < 3.5)
        low_communication_count = sum(1 for s in performance_scores if s.communication_skills_score < 3.5)
        low_product_count = sum(1 for s in performance_scores if s.product_pitch_score < 3.5)
        
        recommendations = []
        
        # High priority recommendations
        if low_objection_count >= len(performance_scores) * 0.4:  # 40% or more need help
            recommendations.append({
                'priority': 'high',
                'title': 'Priority: Objection Handling Training',
                'description': f'{low_objection_count} out of {len(performance_scores)} agents score below 3.5/5 in objection handling. Recommend focused workshop on defusing customer concerns.',
                'action': 'Schedule objection handling workshop'
            })
        
        if low_communication_count >= len(performance_scores) * 0.3:
            recommendations.append({
                'priority': 'medium',
                'title': 'Focus Area: Communication Skills',
                'description': f'Multiple agents would benefit from communication skills coaching to improve rapport building and active listening.',
                'action': 'Implement communication skills training program'
            })
        
        # Leverage strengths
        high_performers = [s for s in performance_scores if s.overall_score >= 4.0]
        if high_performers:
            recommendations.append({
                'priority': 'leverage',
                'title': 'Leverage Top Performers',
                'description': f'{len(high_performers)} agents show excellent performance. Consider peer mentoring program.',
                'action': 'Set up mentoring pairs with top performers'
            })
        
        return jsonify({
            'recommendations': recommendations,
            'total_analyzed': len(performance_scores),
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    print("🚀 Starting AIA Agent Performance Dashboard...")
    print(f"📊 Performance Analyzer Status: {'✅ Connected' if performance_analyzer else '❌ Not Available'}")
    print("💡 Dashboard will load instantly with cached data")
    print("🔄 Click 'Refresh AI Insights' to run new AI analysis")
    app.run(debug=True, host='0.0.0.0', port=5050)
