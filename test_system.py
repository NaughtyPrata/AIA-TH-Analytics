#!/usr/bin/env python3
"""
Quick Test - Simple validation of the AI system
"""

from simple_ai_analyzer import SimpleAIAAnalyzer
import json

def test_system():
    """Test the basic functionality"""
    
    print("🧪 AIA Analytics - System Test")
    print("=" * 40)
    
    try:
        # Test 1: Initialize
        print("\n1️⃣ Testing system initialization...")
        analyzer = SimpleAIAAnalyzer()
        print("✅ System initialized successfully")
        
        # Test 2: Load data
        print("\n2️⃣ Testing data loading...")
        stats = analyzer.get_basic_stats()
        print(f"✅ Data loaded: {stats['total_messages']} messages, {stats['unique_conversations']} conversations")
        
        # Test 3: Find a conversation with content
        print("\n3️⃣ Finding suitable conversation for analysis...")
        df = analyzer.load_transcript_data(limit=100)
        
        # Find conversations with actual dialogue
        conversation_lengths = df.groupby('Conversation ID').size()
        suitable_conversations = conversation_lengths[conversation_lengths >= 3].index.tolist()
        
        if suitable_conversations:
            test_conv = suitable_conversations[0]
            print(f"✅ Found suitable conversation: {test_conv}")
            
            # Show conversation content
            conv_data = df[df['Conversation ID'] == test_conv]
            print(f"📝 Conversation preview ({len(conv_data)} messages):")
            for i, (_, row) in enumerate(conv_data.iterrows()):
                if i < 3:  # Show first 3 messages
                    print(f"   {row['Message Role']}: {row['Message Text'][:50]}...")
            
            # Test 4: AI Analysis (if API available)
            print(f"\n4️⃣ Testing AI analysis on {test_conv}...")
            insight = analyzer.analyze_conversation(test_conv)
            
            print(f"✅ AI Analysis completed:")
            print(f"   Intent: {insight.customer_intent[:80]}...")
            print(f"   Sentiment: {insight.sentiment}")
            print(f"   Issues: {len(insight.issues_identified)} identified")
            
        else:
            print("⚠️ No suitable conversations found for AI analysis")
        
        print("\n" + "=" * 40)
        print("🎉 SYSTEM TEST COMPLETED SUCCESSFULLY!")
        print("=" * 40)
        
        return True
        
    except Exception as e:
        print(f"\n❌ SYSTEM TEST FAILED: {e}")
        print("\nThis might be due to:")
        print("- OpenAI API key issues")
        print("- Network connectivity")
        print("- Data format problems")
        return False

if __name__ == "__main__":
    success = test_system()
    exit(0 if success else 1)
