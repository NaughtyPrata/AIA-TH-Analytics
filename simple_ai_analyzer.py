#!/usr/bin/env python3
"""
AIA Analytics - Simple AI Analyzer
Alternative implementation using requests for OpenAI API
"""

import os
import pandas as pd
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
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

class SimpleAIAAnalyzer:
    def __init__(self):
        """Initialize the Simple AIA Analytics AI Analyzer"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        self.knowledge_base = self._load_knowledge_base()
        self.transcript_path = 'log/transcript.csv'
        print("✅ Simple AI Analyzer initialized successfully")
        
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
            
            # Filter out N/A entries and ensure we have actual conversations
            df = df[df['Message Role'] != 'N/A']
            df = df[df['Message Text'].notna()]
            df = df[df['Message Text'] != 'No transcript available']
            print(f"📊 After filtering: {len(df)} rows")
            
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
        """Make OpenAI API request using requests library"""
        payload = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "You are an expert insurance industry analyst specializing in customer conversation analysis. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.3
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️ API Request Error: {e}")
            return json.dumps({
                "error": f"API Request Error: {str(e)}",
                "customer_intent": "Unable to analyze due to API error",
                "sentiment": "unknown",
                "product_interest": [],
                "issues_identified": [f"API Error: {str(e)[:100]}"],
                "resolution_status": "unknown",
                "recommendations": ["Check OpenAI API key and network connection"]
            })
        except Exception as e:
            print(f"⚠️ Unexpected Error: {e}")
            return json.dumps({
                "error": f"Unexpected Error: {str(e)}",
                "customer_intent": "Unable to analyze",
                "sentiment": "unknown",
                "product_interest": [],
                "issues_identified": [f"Error: {str(e)[:100]}"],
                "resolution_status": "unknown",
                "recommendations": ["Check system configuration"]
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
        {conversation_text[:2000]}  # Limit conversation length
        
        KNOWLEDGE BASE CONTEXT:
        {self.knowledge_base[:2000]}  # Limit knowledge base length
        
        Please provide a comprehensive analysis in JSON format with these exact fields:
        {{
            "customer_intent": "What is the customer trying to achieve?",
            "sentiment": "positive/neutral/negative/frustrated",
            "product_interest": ["list", "of", "products"],
            "issues_identified": ["list", "of", "issues"],
            "resolution_status": "resolved/partially_resolved/unresolved/ongoing",
            "recommendations": ["list", "of", "recommendations"]
        }}
        
        Focus on identifying sales opportunities, customer pain points, and service quality.
        Ensure your response is valid JSON.
        """
        
        try:
            response_content = self._make_openai_request(prompt, max_tokens=800)
            
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
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error for {conversation_id}: {e}")
            print(f"Raw response: {response_content[:200]}...")
            return ConversationInsight(
                conversation_id=conversation_id,
                customer_intent="JSON parsing failed",
                sentiment="unknown",
                product_interest=[],
                issues_identified=[f"JSON error: {str(e)}"],
                resolution_status="unknown",
                recommendations=["Fix JSON response format"]
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
            "sample_conversations": df['Conversation ID'].unique()[:5].tolist(),
            "avg_messages_per_conversation": round(len(df) / df['Conversation ID'].nunique(), 1)
        }
        
        return stats
    
    def analyze_sample_conversations(self, num_conversations: int = 3) -> List[ConversationInsight]:
        """Analyze a few sample conversations to test the system"""
        df = self.load_transcript_data()
        
        # Get conversations that have actual content
        conversation_lengths = df.groupby('Conversation ID').size()
        suitable_conversations = conversation_lengths[conversation_lengths >= 2].index.tolist()
        
        if not suitable_conversations:
            print("❌ No suitable conversations found for analysis")
            return []
        
        sample_convs = suitable_conversations[:num_conversations]
        insights = []
        
        for conv_id in sample_convs:
            try:
                print(f"\n🔍 Analyzing sample conversation: {conv_id}")
                insight = self.analyze_conversation(conv_id)
                insights.append(insight)
                print(f"✅ Completed analysis of {conv_id}")
                print(f"   Intent: {insight.customer_intent[:100]}...")
                print(f"   Sentiment: {insight.sentiment}")
            except Exception as e:
                print(f"❌ Failed to analyze {conv_id}: {e}")
        
        return insights
    
    def generate_conversation_summary(self, limit: int = 10) -> str:
        """Generate AI-powered summary of conversations"""
        df = self.load_transcript_data()
        
        # Get recent conversations with actual content
        unique_convs = df['Conversation ID'].unique()[:limit]
        df_sample = df[df['Conversation ID'].isin(unique_convs)]
        
        # Group by conversation and create summary text
        conversations_text = ""
        for conv_id in df_sample['Conversation ID'].unique()[:5]:  # Limit to 5 for API efficiency
            conv_data = df_sample[df_sample['Conversation ID'] == conv_id]
            conversations_text += f"\n--- Conversation {conv_id} ---\n"
            for _, row in conv_data.iterrows():
                conversations_text += f"{row['Message Role']}: {row['Message Text']}\n"
        
        prompt = f"""
        Analyze these customer service conversations from AIA Thailand life insurance and provide:
        
        ## EXECUTIVE SUMMARY
        ## KEY TRENDS AND PATTERNS  
        ## CUSTOMER SATISFACTION INSIGHTS
        ## PRODUCT INTEREST ANALYSIS
        ## OPERATIONAL RECOMMENDATIONS
        ## SALES OPPORTUNITIES IDENTIFIED
        
        CONVERSATIONS:
        {conversations_text[:3000]}  # Truncate for token limits
        
        KNOWLEDGE BASE CONTEXT:
        {self.knowledge_base[:1500]}
        
        Provide actionable insights for management in a clear, structured format.
        """
        
        return self._make_openai_request(prompt, max_tokens=1500)
    
    def identify_product_opportunities(self, limit: int = 15) -> str:
        """Identify sales and product opportunities"""
        df = self.load_transcript_data()
        unique_convs = df['Conversation ID'].unique()[:limit]
        
        opportunities_text = ""
        for conv_id in unique_convs[:8]:  # Limit for API costs
            conv_data = df[df['Conversation ID'] == conv_id]
            conv_text = ""
            for _, row in conv_data.iterrows():
                conv_text += f"{row['Message Role']}: {row['Message Text']}\n"
            opportunities_text += f"\n--- Conversation {conv_id} ---\n{conv_text}"
        
        prompt = f"""
        Analyze these customer conversations for sales and product opportunities:
        
        CONVERSATIONS:
        {opportunities_text[:3500]}
        
        AIA PRODUCTS KNOWLEDGE:
        {self.knowledge_base[:1500]}
        
        Identify and provide specific recommendations for:
        
        ## UPSELLING OPPORTUNITIES
        ## CROSS-SELLING POTENTIAL  
        ## PRODUCT GAPS OR UNMET CUSTOMER NEEDS
        ## PRICING CONCERNS OR COMPETITIVE THREATS
        ## CUSTOMER LIFECYCLE INSIGHTS
        ## SPECIFIC ACTION ITEMS FOR SALES TEAM
        
        Provide concrete, actionable recommendations with specific customer segments and products.
        """
        
        return self._make_openai_request(prompt, max_tokens=1200)
    
    def generate_full_report(self, output_file: str = "ai_analysis_report.md") -> str:
        """Generate comprehensive AI analysis report"""
        stats = self.get_basic_stats()
        
        print("📊 Generating data overview...")
        print("📝 Creating executive summary...")
        summary = self.generate_conversation_summary(limit=15)
        
        print("💡 Analyzing product opportunities...")
        opportunities = self.identify_product_opportunities(limit=20)
        
        print("🔍 Analyzing sample conversations...")
        sample_insights = self.analyze_sample_conversations(num_conversations=3)
        
        report_content = f"""# AIA Analytics - AI Analysis Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Data Overview
- **Total Messages**: {stats.get('total_messages', 'N/A'):,}
- **Unique Conversations**: {stats.get('unique_conversations', 'N/A'):,}
- **Date Range**: {stats.get('date_range', {}).get('start', 'N/A')} to {stats.get('date_range', {}).get('end', 'N/A')}
- **Average Messages per Conversation**: {stats.get('avg_messages_per_conversation', 'N/A')}
- **Message Roles Distribution**: {stats.get('message_roles', {})}

## Executive Summary & Trends Analysis
{summary}

## Product Opportunities Analysis
{opportunities}

## Sample Conversation Analysis

"""
        
        for i, insight in enumerate(sample_insights, 1):
            report_content += f"""
### Sample Conversation {i}: {insight.conversation_id}
- **Customer Intent**: {insight.customer_intent}
- **Sentiment**: {insight.sentiment}
- **Product Interest**: {', '.join(insight.product_interest) if insight.product_interest else 'None identified'}
- **Issues**: {', '.join(insight.issues_identified) if insight.issues_identified else 'None'}
- **Resolution Status**: {insight.resolution_status}
- **Recommendations**: 
"""
            for rec in insight.recommendations:
                report_content += f"  - {rec}\n"
        
        report_content += f"""

## Key Metrics Summary
- **Total Conversations Analyzed**: {len(sample_insights)}
- **Sentiment Distribution**: {dict(pd.Series([i.sentiment for i in sample_insights]).value_counts())}
- **Most Common Issues**: {list(set([issue for insight in sample_insights for issue in insight.issues_identified]))[:5]}

---
*Report generated by AIA Analytics Simple AI Analyzer*
*Using OpenAI GPT-4o for conversation analysis*
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
        analyzer = SimpleAIAAnalyzer()
    except Exception as e:
        print(f"❌ Failed to initialize analyzer: {e}")
        return
    
    print("🤖 AIA Analytics - Simple AI Analyzer")
    print("=" * 50)
    
    # Show basic stats first
    stats = analyzer.get_basic_stats()
    print("\n📊 Data Overview:")
    for key, value in stats.items():
        if key != 'sample_conversations':
            print(f"   {key}: {value}")
    
    while True:
        print("\nOptions:")
        print("1. Analyze specific conversation")
        print("2. Analyze sample conversations")
        print("3. Generate conversation summary")
        print("4. Show data statistics")
        print("5. Identify product opportunities")
        print("6. Generate full report")
        print("7. Exit")
        
        choice = input("\nSelect option (1-7): ").strip()
        
        if choice == '1':
            print(f"\nAvailable conversations: {stats.get('sample_conversations', [])}")
            conv_id = input("Enter Conversation ID: ").strip()
            try:
                insight = analyzer.analyze_conversation(conv_id)
                print(f"\n📊 Analysis for {conv_id}:")
                print(f"📝 Intent: {insight.customer_intent}")
                print(f"😊 Sentiment: {insight.sentiment}")
                print(f"📦 Product Interest: {insight.product_interest}")
                print(f"⚠️ Issues: {insight.issues_identified}")
                print(f"✅ Status: {insight.resolution_status}")
                print(f"💡 Recommendations:")
                for rec in insight.recommendations:
                    print(f"   • {rec}")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        elif choice == '2':
            num = int(input("Number of sample conversations to analyze (default 3): ") or "3")
            print(f"\n🔍 Analyzing {num} sample conversations...")
            insights = analyzer.analyze_sample_conversations(num_conversations=num)
            print(f"\n✅ Analyzed {len(insights)} conversations successfully")
        
        elif choice == '3':
            limit = int(input("Number of conversations to include (default 10): ") or "10")
            print("\n📝 Generating summary...")
            summary = analyzer.generate_conversation_summary(limit=limit)
            print(summary)
        
        elif choice == '4':
            stats = analyzer.get_basic_stats()
            print("\n📈 Data Statistics:")
            print(json.dumps(stats, indent=2, default=str))
        
        elif choice == '5':
            limit = int(input("Number of conversations to analyze (default 15): ") or "15")
            print("\n💡 Identifying product opportunities...")
            opportunities = analyzer.identify_product_opportunities(limit=limit)
            print(opportunities)
        
        elif choice == '6':
            filename = input("Output filename (default: ai_analysis_report.md): ").strip() or "ai_analysis_report.md"
            print("\n📄 Generating full report...")
            result = analyzer.generate_full_report(filename)
            print(result)
        
        elif choice == '7':
            print("👋 Goodbye!")
            break
        
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
