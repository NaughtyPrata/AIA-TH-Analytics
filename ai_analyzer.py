#!/usr/bin/env python3
"""
AIA Analytics AI Analyzer
Analyzes customer conversations and provides insights using OpenAI GPT-4o
"""

import os
import pandas as pd
import openai
from datetime import datetime, timedelta
import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import glob
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
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.knowledge_base = self._load_knowledge_base()
        self.transcript_path = 'log/transcript.csv'
        
    def _load_knowledge_base(self) -> str:
        """Load all knowledge base files into a single string"""
        knowledge_content = ""
        kb_path = Path("AIA_PayLifePlus_Brochure")
        
        if kb_path.exists():
            for md_file in sorted(kb_path.glob("*.md")):
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    knowledge_content += f"\n\n--- {md_file.name} ---\n{content}"
        
        return knowledge_content
    
    def load_transcript_data(self, limit: Optional[int] = None) -> pd.DataFrame:
        """Load and preprocess transcript data"""
        try:
            df = pd.read_csv(self.transcript_path)
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            # Filter out N/A entries
            df = df[df['Message Role'] != 'N/A']
            
            if limit:
                df = df.head(limit)
                
            return df
        except Exception as e:
            print(f"Error loading transcript data: {e}")
            return pd.DataFrame()
    
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
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert insurance industry analyst specializing in customer conversation analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            # Parse JSON response
            analysis = json.loads(response.choices[0].message.content)
            
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
            print(f"Error analyzing conversation {conversation_id}: {e}")
            return ConversationInsight(
                conversation_id=conversation_id,
                customer_intent="Analysis failed",
                sentiment="unknown",
                product_interest=[],
                issues_identified=[f"Analysis error: {str(e)}"],
                resolution_status="unknown",
                recommendations=[]
            )
    
    def generate_conversation_summary(self, conversation_ids: List[str] = None, limit: int = 10) -> str:
        """Generate AI-powered summary of conversations"""
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
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a senior business analyst specializing in insurance industry analytics and customer experience optimization."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating summary: {e}"
    
    def analyze_sentiment_trends(self, days_back: int = 7) -> Dict:
        """Analyze sentiment trends over time"""
        df = self.load_transcript_data()
        
        if df.empty:
            return {"error": "No data available"}
        
        # Convert date column
        df['Created At'] = pd.to_datetime(df['Created At'], format='%Y-%m-%d %H:%M:%S (GMT+7)')
        
        # Filter recent data
        cutoff_date = datetime.now() - timedelta(days=days_back)
        recent_df = df[df['Created At'] >= cutoff_date]
        
        # Get unique conversations for analysis
        unique_convs = recent_df['Conversation ID'].unique()[:20]  # Limit for API costs
        
        sentiments = []
        for conv_id in unique_convs:
            try:
                insight = self.analyze_conversation(conv_id)
                sentiments.append({
                    'conversation_id': conv_id,
                    'sentiment': insight.sentiment,
                    'date': recent_df[recent_df['Conversation ID'] == conv_id]['Created At'].iloc[0]
                })
            except Exception as e:
                print(f"Error analyzing {conv_id}: {e}")
                continue
        
        return {
            'sentiment_distribution': pd.Series([s['sentiment'] for s in sentiments]).value_counts().to_dict(),
            'total_analyzed': len(sentiments),
            'period': f"Last {days_back} days"
        }
    
    def identify_product_opportunities(self, limit: int = 20) -> str:
        """Identify sales and product opportunities"""
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
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a senior sales analyst for the insurance industry with expertise in customer lifecycle management and product positioning."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error identifying opportunities: {e}"
    
    def generate_full_report(self, output_file: str = "ai_analysis_report.md") -> str:
        """Generate comprehensive AI analysis report"""
        report_content = f"""# AIA Analytics - AI Analysis Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
{self.generate_conversation_summary(limit=15)}

## Product Opportunities Analysis
{self.identify_product_opportunities(limit=25)}

## Sentiment Analysis
"""
        
        sentiment_data = self.analyze_sentiment_trends(days_back=14)
        report_content += f"""
### Recent Sentiment Trends (Last 14 days)
- **Total Conversations Analyzed**: {sentiment_data.get('total_analyzed', 0)}
- **Sentiment Distribution**: {sentiment_data.get('sentiment_distribution', {})}

"""
        
        # Save report
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return f"Report generated: {output_file}"

def main():
    """Main execution function"""
    analyzer = AIAAnalyzer()
    
    print("🤖 AIA Analytics AI Analyzer")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Analyze specific conversation")
        print("2. Generate conversation summary")
        print("3. Analyze sentiment trends")
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
                print(f"Error: {e}")
        
        elif choice == '2':
            limit = int(input("Number of conversations to analyze (default 10): ") or "10")
            print("\n📝 Generating summary...")
            summary = analyzer.generate_conversation_summary(limit=limit)
            print(summary)
        
        elif choice == '3':
            days = int(input("Days back to analyze (default 7): ") or "7")
            print(f"\n📈 Analyzing sentiment trends for last {days} days...")
            trends = analyzer.analyze_sentiment_trends(days_back=days)
            print(json.dumps(trends, indent=2, default=str))
        
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
