#!/usr/bin/env python3
"""
Quick Analysis Script - Run specific analyses without interactive menu
"""
from ai_analyzer import AIAAnalyzer
import sys

def quick_summary():
    """Generate a quick summary report"""
    analyzer = AIAAnalyzer()
    print("🔍 Quick Analysis Report")
    print("=" * 50)
    
    # Generate summary
    print("\n📊 CONVERSATION SUMMARY:")
    summary = analyzer.generate_conversation_summary(limit=10)
    print(summary)
    
    # Sentiment analysis
    print("\n📈 SENTIMENT TRENDS:")
    sentiment_data = analyzer.analyze_sentiment_trends(days_back=7)
    print(f"Analyzed {sentiment_data.get('total_analyzed', 0)} conversations")
    print(f"Sentiment breakdown: {sentiment_data.get('sentiment_distribution', {})}")
    
    # Product opportunities
    print("\n💡 PRODUCT OPPORTUNITIES:")
    opportunities = analyzer.identify_product_opportunities(limit=15)
    print(opportunities)

def analyze_specific_conversation(conv_id: str):
    """Analyze a specific conversation"""
    analyzer = AIAAnalyzer()
    try:
        insight = analyzer.analyze_conversation(conv_id)
        print(f"\n🔍 Analysis for Conversation {conv_id}")
        print("=" * 50)
        print(f"📝 Customer Intent: {insight.customer_intent}")
        print(f"😊 Sentiment: {insight.sentiment}")
        print(f"📦 Product Interest: {', '.join(insight.product_interest) if insight.product_interest else 'None identified'}")
        print(f"⚠️  Issues Identified: {', '.join(insight.issues_identified) if insight.issues_identified else 'None'}")
        print(f"✅ Resolution Status: {insight.resolution_status}")
        print(f"💡 Recommendations:")
        for rec in insight.recommendations:
            print(f"   • {rec}")
    except Exception as e:
        print(f"❌ Error analyzing conversation {conv_id}: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "summary":
            quick_summary()
        elif sys.argv[1] == "analyze" and len(sys.argv) > 2:
            analyze_specific_conversation(sys.argv[2])
        else:
            print("Usage:")
            print("  python quick_analysis.py summary")
            print("  python quick_analysis.py analyze CONVERSATION_ID")
    else:
        quick_summary()
