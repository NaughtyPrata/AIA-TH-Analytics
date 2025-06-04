#!/usr/bin/env python3
"""
AIA Analytics AI Analyzer - Fixed Version
Analyzes customer conversations and provides insights using OpenAI GPT-4o
"""

import os
import pandas as pd
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

@dataclass
class ConversationInsight:
    conversation_id: str
    customer_intent: str
    sentiment: str
    product_interest: List[str]
    issues_identified: List[str]
    resolution_status: str
    recommendations: List[str]

class AIAAnalyzer:
    def __init__(self):
        """Initialize the AIA Analytics AI Analyzer"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Initialize OpenAI client with error handling
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
            print("✅ OpenAI client initialized successfully")
        except Exception as e:
            print(f"⚠️ Warning: OpenAI client initialization failed: {e}")
            print("📊 Data analysis will work, but AI insights will be limited")
            self.client = None
        
        self.knowledge_base = self._load_knowledge_base()
        self.transcript_path = 'log/transcript.csv'
        
    def _load_knowledge_base(self) -> str:
        """Load all knowledge base files into a single string"""
        knowledge_content = ""
        kb_path = Path("AIA_PayLifePlus_Brochure")
        
        if kb_path.exists():
            for md_file in sorted(kb_path.glob("*.md")):
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        knowledge_content += f"\n\n--- {md_file.name} ---\n{content}"
                except Exception as e:
                    print(f"⚠️ Error loading {md_file}: {e}")
        
        print(f"📚 Knowledge base loaded: {len(knowledge_content)} characters")
        return knowledge_content
    
    def load_transcript_data(self, limit: Optional[int] = None) -> pd.DataFrame:
        """Load and preprocess transcript data"""
        try:
            df = pd.read_csv(self.transcript_path)
            print(f"📥 Raw data loaded: {len(df)} rows")
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            # Filter out N/A entries
            df = df[df['Message Role'] != 'N/A']
            print(f"📊 After filtering N/A: {len(df)} rows")
            
            # Convert date column
            if 'Created At' in df.columns:
                df['Created At'] = pd.to_datetime(df['Created At'], format='%Y-%m-%d %H:%M:%S (GMT+7)', errors='coerce')
            
            if limit:
                df = df.head(limit)
                print(f"📋 Limited to: {len(df)} rows")
                
            return df
        except Exception as e:
            print(f"❌ Error loading transcript data: {e}")
            return pd.DataFrame()
    
    def _make_openai_request(self, prompt: str, max_tokens: int = 1000) -> str:
        """Make OpenAI API request with error handling"""
        if not self.client:
            return json.dumps({
                "error": "OpenAI client not available",
                "customer_intent": "Unable to analyze - API client error",
                "sentiment": "unknown",
                "product_interest": [],
                "issues_identified": ["API unavailable"],
                "resolution_status": "unknown",
                "recommendations": ["Fix OpenAI client setup"]
            })
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert insurance industry analyst specializing in customer conversation analysis. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"⚠️ OpenAI API Error: {e}")
            return json.dumps({
                "error": f"API Error: {str(e)}",
                "customer_intent": "Unable to analyze due to API error",
                "sentiment": "unknown",
                "product_interest": [],
                "issues_identified": [f"API Error: {str(e)[:100]}"],
                "resolution_status": "unknown",
                "recommendations": ["Check OpenAI API key and credits"]
            })
    
    def analyze_conversation(self, conversation_id: str) -> ConversationInsight:
        """Analyze a single conversation using GPT-4o"""
        # Get conversation data
        df = self.load_transcript_data()
        conv_data = df[df['Conversation ID'] == conversation_id]
        
        if conv_data.empty:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        # Prepare conversation text
        conversation_text = ""
        for _, row in conv_data.iterrows():
            role = row['Message Role']
            text = row['Message Text']
            conversation_text += f"{role}: {text}\n"
        
        print(f"🔍 Analyzing conversation {conversation_id} ({len(conversation_text)} characters)")
        
        # Create analysis prompt
        prompt = f"""
        Analyze this customer service conversation from AIA Thailand life insurance.
        
        CONVERSATION:
        {conversation_text}
        
        KNOWLEDGE BASE CONTEXT:
        {self.knowledge_base[:3000]}  # Truncate for token limits
        
        Please provide a comprehensive analysis in JSON format with these fields:
        - customer_intent: What is the customer trying to achieve?
        - sentiment: Overall sentiment (positive/neutral/negative/frustrated)
        - product_interest: List of insurance products mentioned or implied interest
        - issues_identified: List of problems or concerns raised
        - resolution_status: Was the issue resolved? (resolved/partially_resolved/unresolved/ongoing)
        - recommendations: List of actionable recommendations for improvement
        
        Focus on identifying sales opportunities, customer pain points, and service quality.
        """
        
        try:
            response_content = self._make_openai_request(prompt, max_tokens=1000)
            
            # Parse JSON response
            analysis = json.loads(response_content)
            
            return ConversationInsight(
                conversation_id=conversation_id,
                customer_intent=analysis.get('customer_intent', ''),
                sentiment=analysis.get('sentiment', ''),
                product_interest=analysis.get('product_interest', []),
                issues_identified=analysis.get('issues_identified', []),
                resolution_status=analysis.get('resolution_status', ''),
                recommendations=analysis.get('recommendations', [])
            )
            
        except Exception as e:
            print(f"❌ Error analyzing conversation {conversation_id}: {e}")
            return ConversationInsight(
                conversation_id=conversation_id,
                customer_intent="Analysis failed",
                sentiment="unknown",
                product_interest=[],
                issues_identified=[f"Analysis error: {str(e)}"],
                resolution_status="unknown",
                recommendations=[]
            )
    
    def get_basic_stats(self) -> Dict:
        """Get basic statistics without AI analysis"""
        df = self.load_transcript_data()
        
        if df.empty:
            return {"error": "No data available"}
        
        stats = {
            "total_messages": len(df),
            "unique_conversations": df['Conversation ID'].nunique(),
            "date_range": {
                "start": df['Created At'].min().strftime('%Y-%m-%d') if 'Created At' in df.columns and not df['Created At'].isnull().all() else "Unknown",
                "end": df['Created At'].max().strftime('%Y-%m-%d') if 'Created At' in df.columns and not df['Created At'].isnull().all() else "Unknown"
            },
            "message_roles": df['Message Role'].value_counts().to_dict(),
            "sample_conversations": df['Conversation ID'].unique()[:5].tolist()
        }
        
        return stats
    
    def generate_conversation_summary(self, conversation_ids: List[str] = None, limit: int = 10) -> str:
        """Generate AI-powered summary of conversations"""
        if not self.client:
            return "❌ AI summary unavailable - OpenAI client not initialized"
        
        df = self.load_transcript_data()
        
        if conversation_ids:
            df = df[df['Conversation ID'].isin(conversation_ids)]
        else:
            # Get recent conversations
            unique_convs = df['Conversation ID'].unique()[:limit]
            df = df[df['Conversation ID'].isin(unique_convs)]
        
        # Group by conversation
        conversations_text = ""
        for conv_id in df['Conversation ID'].unique():
            conv_data = df[df['Conversation ID'] == conv_id]
            conversations_text += f"\n--- Conversation {conv_id} ---\n"
            for _, row in conv_data.iterrows():
                conversations_text += f"{row['Message Role']}: {row['Message Text']}\n"
        
        prompt = f"""
        Analyze these customer service conversations from AIA Thailand life insurance and provide:
        
        1. EXECUTIVE SUMMARY
        2. KEY TRENDS AND PATTERNS
        3. CUSTOMER SATISFACTION INSIGHTS
        4. PRODUCT INTEREST ANALYSIS
        5. OPERATIONAL RECOMMENDATIONS
        6. SALES OPPORTUNITIES IDENTIFIED
        
        CONVERSATIONS:
        {conversations_text[:4000]}  # Truncate for token limits
        
        KNOWLEDGE BASE CONTEXT:
        {self.knowledge_base[:2000]}
        
        Provide actionable insights for management.
        """
        
        return self._make_openai_request(prompt, max_tokens=2000)
    
    def identify_product_opportunities(self, limit: int = 20) -> str:
        """Identify sales and product opportunities"""
        if not self.client:
            return "❌ Product opportunity analysis unavailable - OpenAI client not initialized"
        
        df = self.load_transcript_data()
        unique_convs = df['Conversation ID'].unique()[:limit]
        
        opportunities_text = ""
        for conv_id in unique_convs[:10]:  # Limit for API costs
            conv_data = df[df['Conversation ID'] == conv_id]
            conv_text = ""
            for _, row in conv_data.iterrows():
                conv_text += f"{row['Message Role']}: {row['Message Text']}\n"
            opportunities_text += f"\n--- Conversation {conv_id} ---\n{conv_text}"
        
        prompt = f"""
        Analyze these customer conversations for sales and product opportunities:
        
        CONVERSATIONS:
        {opportunities_text[:4000]}
        
        AIA PRODUCTS KNOWLEDGE:
        {self.knowledge_base[:2000]}
        
        Identify:
        1. Upselling opportunities
        2. Cross-selling potential
        3. Product gaps or customer needs not met
        4. Pricing concerns or competitive threats
        5. Customer lifecycle stage and appropriate products
        6. Specific action items for sales team
        
        Provide concrete, actionable recommendations.
        """
        
        return self._make_openai_request(prompt, max_tokens=1500)
    
    def generate_full_report(self, output_file: str = "ai_analysis_report.md") -> str:
        """Generate comprehensive AI analysis report"""
        stats = self.get_basic_stats()
        
        report_content = f"""# AIA Analytics - AI Analysis Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Data Overview
- **Total Messages**: {stats.get('total_messages', 'N/A')}
- **Unique Conversations**: {stats.get('unique_conversations', 'N/A')}
- **Date Range**: {stats.get('date_range', {}).get('start', 'N/A')} to {stats.get('date_range', {}).get('end', 'N/A')}
- **Message Roles**: {stats.get('message_roles', {})}

## Executive Summary
{self.generate_conversation_summary(limit=15)}

## Product Opportunities Analysis
{self.identify_product_opportunities(limit=25)}

## Sample Conversations
{stats.get('sample_conversations', [])}

---
*Report generated by AIA Analytics AI Analyzer*
"""
        
        # Save report
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            return f"✅ Report generated: {output_file}"
        except Exception as e:
            return f"❌ Error saving report: {e}"

def main():
    """Main execution function"""
    try:
        analyzer = AIAAnalyzer()
    except Exception as e:
        print(f"❌ Failed to initialize analyzer: {e}")
        return
    
    print("🤖 AIA Analytics AI Analyzer")
    print("=" * 50)
    
    # Show basic stats first
    stats = analyzer.get_basic_stats()
    print("\n📊 Data Overview:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    while True:
        print("\nOptions:")
        print("1. Analyze specific conversation")
        print("2. Generate conversation summary")
        print("3. Show data statistics")
        print("4. Identify product opportunities")
        print("5. Generate full report")
        print("6. Exit")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == '1':
            conv_id = input("Enter Conversation ID: ").strip()
            try:
                insight = analyzer.analyze_conversation(conv_id)
                print(f"\n📊 Analysis for {conv_id}:")
                print(f"Intent: {insight.customer_intent}")
                print(f"Sentiment: {insight.sentiment}")
                print(f"Product Interest: {insight.product_interest}")
                print(f"Issues: {insight.issues_identified}")
                print(f"Status: {insight.resolution_status}")
                print(f"Recommendations: {insight.recommendations}")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        elif choice == '2':
            limit = int(input("Number of conversations to analyze (default 10): ") or "10")
            print("\n📝 Generating summary...")
            summary = analyzer.generate_conversation_summary(limit=limit)
            print(summary)
        
        elif choice == '3':
            stats = analyzer.get_basic_stats()
            print("\n📈 Data Statistics:")
            print(json.dumps(stats, indent=2, default=str))
        
        elif choice == '4':
            limit = int(input("Number of conversations to analyze (default 20): ") or "20")
            print("\n💡 Identifying product opportunities...")
            opportunities = analyzer.identify_product_opportunities(limit=limit)
            print(opportunities)
        
        elif choice == '5':
            filename = input("Output filename (default: ai_analysis_report.md): ").strip() or "ai_analysis_report.md"
            print("\n📄 Generating full report...")
            result = analyzer.generate_full_report(filename)
            print(result)
        
        elif choice == '6':
            print("👋 Goodbye!")
            break
        
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
