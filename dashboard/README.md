# AIA Analytics Dashboard

A web-based dashboard for analyzing agent performance metrics from transcript data. This dashboard provides visualizations and insights into agent conversations.

## Features

- **Overview Dashboard**: High-level metrics and trends
- **Agent Analysis**: Detailed agent performance metrics 
- **Conversation Analysis**: Drill-down into specific conversations
- **Trend Analysis**: Time-based performance tracking
- **Descriptive Statistics**: Mean, median, standard deviation displays for each metric
- **Correlation Analysis**: Identify relationships between different metrics
- **Agent Clustering**: Group agents by performance patterns
- **Session Variability**: Measure consistency across sessions

## Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML with Tailwind CSS, Chart.js
- **Data Processing**: Python with pandas
- **Styling**: ITCSS methodology

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd AIA-TH-Analytics/dashboard
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the Dashboard

1. Start the Flask development server:
   ```
   python app.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Project Structure

```
dashboard/
├── app.py                  # Flask application
├── static/                 # Static assets
│   ├── css/
│   │   └── main.css        # Main CSS file (ITCSS)
│   ├── js/
│   │   └── main.js         # Main JavaScript file
│   └── fonts/              # Font files
├── templates/              # HTML templates
│   ├── base.html           # Base template
│   ├── index.html          # Dashboard home
│   ├── agent_detail.html   # Agent details
│   └── conversation_detail.html  # Conversation details
└── requirements.txt        # Python dependencies
```

## Data Source

The dashboard analyzes transcript data from `log/transcript.csv`, which contains conversation logs with the following fields:
- Conversation ID
- Created At
- Agent ID
- Message Role
- Message Text

## License

[License information] 