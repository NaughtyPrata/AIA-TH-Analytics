# AIA Analytics - AI Conversation Analyzer

🤖 **Advanced AI-powered conversation analysis for AIA Thailand customer service data using OpenAI GPT-4o**

## Overview

This AI analyzer provides comprehensive insights into customer conversations, sentiment analysis, product opportunities identification, and operational recommendations using OpenAI's GPT-4o model combined with your AIA PayLifePlus knowledge base.

## Features

- 🔍 **Individual Conversation Analysis**: Deep dive into specific customer interactions
- 📊 **Sentiment Trend Analysis**: Track customer satisfaction over time
- 💡 **Product Opportunity Identification**: Find upselling and cross-selling opportunities
- 📈 **Executive Reporting**: Generate comprehensive management reports
- 🎯 **Intent Recognition**: Understand what customers are trying to achieve
- ⚠️ **Issue Detection**: Identify and track customer problems
- 💼 **Knowledge Base Integration**: Leverage AIA product information for context

## Quick Start

### 1. Setup
```bash
# Run the setup script
./scripts/setup.sh
```

### 2. Usage Options

#### Interactive Analysis
```bash
python3 src/ai_analyzer.py
```

#### Quick Summary
```bash
python3 src/quick_analysis.py summary
```

#### Analyze Specific Conversation
```bash
python3 src/quick_analysis.py analyze AIA123456
```

#### Jupyter Notebook (Interactive)
```bash
jupyter notebook src/analysis_notebook.ipynb
```

## File Structure

```
AIA-TH-Analytics/
├── .env                           # OpenAI API key
├── README.md                      # Main documentation
├── requirements.txt               # Python dependencies
├── src/                           # Source code
│   ├── ai_analyzer.py             # Main analyzer class
│   ├── ai_analyzer_fixed.py       # Fixed version of analyzer
│   ├── simple_ai_analyzer.py      # Simplified analyzer version
│   ├── quick_analysis.py          # Quick analysis scripts
│   ├── analysis_notebook.ipynb    # Interactive Jupyter notebook
│   ├── demo.py                    # Demo application
│   └── test_system.py             # Test utilities
├── scripts/                       # Shell scripts
│   ├── setup.sh                   # Setup script
│   └── startup.sh                 # Startup script
├── templates/                     # Template files
│   └── agent_performance_template.json  # Agent performance template
├── docs/                          # Documentation
│   ├── DEPLOYMENT_COMPLETE.md     # Deployment documentation
│   ├── SYSTEM_READY.md            # System readiness documentation
│   └── various reports            # Analysis reports
├── dashboard/                     # Dashboard application
├── log/                           # Log files
│   └── transcript.csv             # Conversation data
└── AIA_PayLifePlus_Brochure/      # Knowledge base
    ├── page_001.md
    ├── page_002.md
    └── ...
```

## Analysis Capabilities

### 1. Conversation Insights
- **Customer Intent**: What the customer is trying to achieve
- **Sentiment Analysis**: positive/neutral/negative/frustrated
- **Product Interest**: Insurance products mentioned or implied
- **Issues Identified**: Problems or concerns raised
- **Resolution Status**: resolved/partially_resolved/unresolved/ongoing
- **Recommendations**: Actionable improvement suggestions

### 2. Trend Analysis
- Sentiment trends over time
- Product interest patterns
- Issue frequency analysis
- Resolution rate tracking

### 3. Business Intelligence
- Sales opportunity identification
- Upselling/cross-selling potential
- Customer lifecycle insights
- Competitive threat detection
- Operational efficiency recommendations

## Data Format

Your transcript.csv should contain:
- `Conversation ID`: Unique identifier
- `Created At`: Timestamp in format "YYYY-MM-DD HH:MM:SS (GMT+7)"
- `Agent ID`: Agent identifier
- `Message Role`: Customer/Agent/System
- `Message Text`: Actual conversation content

## Sample Output

```
🔍 Analysis for AIA123456:
Intent: Customer inquiring about life insurance premium payment options
Sentiment: neutral
Product Interest: ['AIA PayLifePlus', 'Life Insurance']
Issues: ['Confusion about payment terms', 'Pricing concerns']
Status: partially_resolved
Recommendations: 
  • Follow up with detailed payment schedule
  • Provide competitor comparison
  • Schedule product demo call
```

## API Usage Examples

```python
from src.ai_analyzer import AIAAnalyzer

# Initialize
analyzer = AIAAnalyzer()

# Analyze single conversation
insight = analyzer.analyze_conversation('AIA123456')
print(f"Customer Intent: {insight.customer_intent}")
print(f"Sentiment: {insight.sentiment}")

# Generate summary report
summary = analyzer.generate_conversation_summary(limit=20)
print(summary)

# Identify opportunities
opportunities = analyzer.identify_product_opportunities(limit=25)
print(opportunities)
```

## Configuration

### Environment Variables (.env)
```
OPENAI_API_KEY=your_openai_api_key_here
```

### Customization
You can modify the analysis prompts in `ai_analyzer.py` to:
- Add new analysis dimensions
- Include additional product information
- Customize sentiment categories
- Adjust recommendation types

## Cost Considerations

- GPT-4o API calls are used for analysis
- Typical cost: ~$0.01-0.05 per conversation analyzed
- Batch processing recommended for large datasets
- Use `limit` parameters to control API usage

## Troubleshooting

### Common Issues

1. **"No data available"**: Check that transcript.csv exists and has correct format
2. **API errors**: Verify OpenAI API key in .env file
3. **Empty analysis**: Ensure conversations have actual message content (not "N/A")

### Performance Tips

- Use smaller batch sizes (10-20 conversations) for faster results
- Implement caching for repeated analyses
- Monitor API rate limits

## Support

For questions or issues:
1. Check the error messages in console output
2. Verify your data format matches expected structure
3. Ensure OpenAI API key has sufficient credits
4. Review the sample outputs in analysis_notebook.ipynb

## License

Internal use for AIA Thailand analytics purposes.

---

*Generated by Claude AI Assistant - Optimized for AIA Thailand customer service analytics*
