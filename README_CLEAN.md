# AIA Analytics Dashboard - Clean Version

## 🎯 What This Is
This dashboard analyzes conversation logs between AIA Human Agents and Virtual AI Customers for training purposes.

## 📁 Project Structure
```
AIA-TH-Analytics/
├── startup                # 🚀 MAIN STARTUP SCRIPT (run this!)
├── dashboard/
│   ├── app.py            # 🎯 Main application (lazy loading version)
│   ├── templates/        # HTML templates
│   └── old_versions/     # 📦 Previous versions (archived)
├── log/
│   └── transcript.csv    # 💬 Conversation data
├── .env                  # 🔑 API keys (OPENAI_API_KEY)
└── simple_ai_analyzer.py # 🤖 AI analysis engine
```

## 🚀 Quick Start

### 1. Start the Dashboard
```bash
./startup
```

### 2. Open in Browser
- **Main Dashboard**: http://localhost:5801/
- **Conversations**: http://localhost:5801/conversations

## ✨ Features

### Dashboard Tab
- **Performance Overview**: Agent stats, skill categories, trends
- **Top Performers**: Best performing agents
- **AI Actions**: Generate reports, refresh insights

### Conversations Tab  
- **Lazy Loading**: Only loads 10 conversations initially
- **On-Demand Analysis**: Click "Click to analyze" for AI insights
- **Pagination**: Navigate through all 470+ conversations
- **Search & Filter**: Find specific conversations
- **Real-time**: Fast loading, responsive interface

## 🎯 How It Works

### Performance Benefits
- **Before**: Loaded 1000+ conversations, analyzed all upfront (30+ seconds)
- **After**: Loads 10 conversations, analyzes on-demand (<2 seconds)

### AI Analysis
- Click "Click to analyze" on any conversation
- Gets customer intent, sentiment, issues, resolution status
- Results are cached for future viewing
- Uses rule-based analysis with OpenAI GPT-4 fallback

## 🔧 Configuration

### Required Environment Variables
```bash
OPENAI_API_KEY=your_key_here  # For AI analysis features
```

### Data Requirements
- Place conversation logs in `log/transcript.csv`
- CSV should have columns: Conversation ID, Created At, Agent ID, Message Role, Message Text

## 🛠️ Troubleshooting

### Port Already in Use
The startup script has aggressive port cleanup, but if needed:
```bash
# Manual port cleanup
sudo lsof -i :5801
sudo kill -9 <PID>
```

### Missing Dependencies
```bash
cd dashboard
pip3 install -r requirements.txt
```

### No Data Showing
- Check if `log/transcript.csv` exists
- Verify CSV has the correct column names
- Check browser console for errors

## 📊 Archive

Previous versions are in `dashboard/old_versions/`:
- `app_original.py` - Your original version
- `fixed_app.py` - Bug fixes
- `optimized_app.py` - Performance improvements  
- `performance_app.py` - Performance focused

## 🎉 That's It!

Just run `./startup` and you're good to go!

**NEW FEATURES:**
- ✅ Script renamed to `startup` (shorter!)
- ✅ Port changed to **5801** (avoiding conflicts)
- ✅ **Aggressive port cleanup** (kills stubborn processes)
- ✅ No more port conflicts or startup issues!
