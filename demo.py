#!/usr/bin/env python3
"""
AIA Analytics - Demo Script
Quick demonstration of AI conversation analysis capabilities
"""

from simple_ai_analyzer import SimpleAIAAnalyzer
import json

def run_demo():
    """Run a comprehensive demo of the AIA Analytics system"""
    
    print("🎯 AIA Analytics AI Analyzer - DEMO")
    print("=" * 60)
    
    try:
        # Initialize analyzer
        print("\n1️⃣ INITIALIZING SYSTEM...")
        analyzer = SimpleAIAAnalyzer()
        
        # Show basic statistics
        print("\n2️⃣ DATA OVERVIEW...")
        stats = analyzer.get_basic_stats()
        print(f"📊 Total Messages: {stats['total_messages']:,}")
        print(f"💬 Unique Conversations: {stats['unique_conversations']:,}")
        print(f"📅 Date Range: {stats['date_range']['start']} to {stats['date_range']['end']}")
        print(f"📈 Avg Messages/Conversation: {stats['avg_messages_per_conversation']}")
        print(f"👥 Message Roles: {stats['message_roles']}")
        
        # Test AI analysis on sample conversation
        print("\n3️⃣ AI CONVERSATION ANALYSIS DEMO...")
        sample_conv_id = stats['sample_conversations'][0]
        print(f"🔍 Analyzing conversation: {sample_conv_id}")
        
        insight = analyzer.analyze_conversation(sample_conv_id)
        
        print(f"\n📋 ANALYSIS RESULTS:")
        print(f"🎯 Customer Intent: {insight.customer_intent}")
        print(f"😊 Sentiment: {insight.sentiment}")
        print(f"📦 Product Interest: {insight.product_interest}")
        print(f"⚠️ Issues Identified: {insight.issues_identified}")
        print(f"✅ Resolution Status: {insight.resolution_status}")
        print(f"💡 AI Recommendations:")
        for i, rec in enumerate(insight.recommendations, 1):
            print(f"   {i}. {rec}")
        
        # Generate executive summary
        print("\n4️⃣ EXECUTIVE SUMMARY GENERATION...")
        print("🤖 Generating AI-powered executive summary...")
        summary = analyzer.generate_conversation_summary(limit=8)
        print("\n📊 EXECUTIVE INSIGHTS:")
        print(summary)
        
        # Identify opportunities
        print("\n5️⃣ PRODUCT OPPORTUNITY ANALYSIS...")
        print("💡 Identifying sales and product opportunities...")
        opportunities = analyzer.identify_product_opportunities(limit=10)
        print("\n🚀 BUSINESS OPPORTUNITIES:")
        print(opportunities)
        
        # Generate full report
        print("\n6️⃣ COMPREHENSIVE REPORT GENERATION...")
        report_filename = f"demo_report_{stats['unique_conversations']}_conversations.md"
        result = analyzer.generate_full_report(report_filename)
        print(result)
        
        print("\n" + "=" * 60)
        print("✅ DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\n🎉 KEY ACHIEVEMENTS:")
        print("✓ Successfully analyzed customer conversation data")
        print("✓ Generated AI-powered insights using GPT-4o")
        print("✓ Identified customer sentiment and intent")
        print("✓ Discovered product opportunities and business insights")
        print("✓ Created comprehensive management report")
        print(f"✓ Processed {stats['total_messages']:,} messages from {stats['unique_conversations']} conversations")
        
        print(f"\n📄 Full report saved as: {report_filename}")
        print("\n🚀 Your AIA Analytics AI system is ready for production use!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("Please check your OpenAI API key and data files.")

if __name__ == "__main__":
    run_demo()
