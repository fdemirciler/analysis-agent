# Financial Analysis Agent

An agentic AI workflow for financial data analysis built by @fdemirciler.

## Overview

This application provides an intelligent financial data analysis platform that allows users to upload financial datasets and interact with them through natural language queries. The system leverages Large Language Models (LLMs) to interpret user intent and automatically route queries to specialized analysis tools.

## 🚀 Features

### Core Functionality
- **File Upload**: Support for CSV and Excel financial data files
- **Natural Language Interface**: Chat-based interaction for querying data
- **Variance Analysis**: Automated comparison between time periods with significance thresholds
- **Real-time Communication**: WebSocket-based interface for instant responses
- **Session Management**: Persistent user sessions with conversation history

### Technical Features
- **Multi-LLM Support**: Flexible provider system (Gemini, OpenAI)
- **Data Profiling**: Automatic detection of time periods, metrics, and data structure
- **Error Handling**: Robust error handling with retry mechanisms
- **Responsive UI**: Modern, mobile-friendly web interface

## 🏗️ Architecture

### Backend Components

#### Core Modules
- **`app/core/orchestrator.py`**: Main workflow coordinator
- **`app/core/data_profiler.py`**: Automatic data structure detection
- **`app/core/session.py`**: User session management

#### LLM Integration
- **`app/llm/provider.py`**: Abstract LLM provider interface
- **`app/llm/gemini.py`**: Google Gemini implementation
- **`app/llm/openai.py`**: OpenAI implementation

#### Analysis Tools
- **`app/tools/base.py`**: Base class for analysis tools
- **`app/tools/variance.py`**: Variance analysis implementation
- **`app/tools/preprocess.py`**: Data preprocessing utilities

#### API Layer
- **`app/api/websocket.py`**: WebSocket communication handler
- **`app/main.py`**: FastAPI application entry point

### Frontend Components
- **`static/index.html`**: Main application interface
- **`static/style.css`**: Responsive styling
- **`static/app.js`**: WebSocket client and UI interactions

### Data Flow
1. User uploads financial data file
2. Data profiler analyzes structure and identifies periods/metrics
3. User submits natural language query
4. LLM interprets query and selects appropriate tool
5. Analysis tool processes data with specified parameters
6. LLM formats results into natural language response
7. Response displayed in chat interface

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.8+
- LLM API key (Gemini or OpenAI)

### Installation Steps
1. **Clone the repository**
   ```bash
   git clone https://github.com/fdemirciler/analysis-agent.git
   cd analysis-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   Create a `.env` file with your LLM configuration:
   ```env
   LLM_PROVIDER=gemini  # or 'openai'
   LLM_API_KEY=your_api_key_here
   LLM_MODEL=gemini-2.5-flash  # or 'gpt-4', 'gpt-3.5-turbo'
   LLM_TEMPERATURE=0.7
   LLM_MAX_TOKENS=8192
   PORT=8000
   DEBUG=false
   ```

4. **Run the application**
   ```bash
   python -m app.main
   ```

5. **Access the interface**
   Open http://localhost:8000 in your browser

## 📊 Usage Examples

### Supported Data Formats
The system works best with financial data in wide format:
- First column: Metric names (e.g., "Revenue", "Operating Expenses")
- Subsequent columns: Time periods (e.g., "2022", "2023", "2024")

### Example Queries
- **"Compare the last two periods and perform a variance analysis"**
  - Automatically identifies most recent periods
  - Calculates absolute and percentage variances
  - Highlights significant changes above threshold

- **"Show me variance line by line in the same P&L format"**
  - Provides detailed variance breakdown
  - Maintains original financial statement structure

- **"What metrics showed the largest percentage increase?"**
  - Ranks metrics by variance magnitude
  - Focuses on growth indicators

## 🔧 Technical Implementation Details

### Key Components Implemented

#### 1. Data Profiling System
- Automatic detection of wide vs. long format data
- Period identification using regex patterns
- Metric extraction and validation
- Sample data generation for LLM context

#### 2. LLM Integration Architecture
- Provider abstraction for multi-LLM support
- JSON extraction from LLM responses
- Retry logic with exponential backoff
- Context-aware prompt engineering

#### 3. WebSocket Communication
- Real-time bidirectional communication
- Session-based state management
- File upload handling with base64 encoding
- Error handling and retry mechanisms

#### 4. Analysis Tool Framework
- Pydantic-based input/output validation
- Extensible tool registration system
- Standardized execution interface
- Type-safe parameter handling

### Bug Fixes Implemented
1. **DataFrame Boolean Context Error**: Fixed pandas DataFrame evaluation in boolean context
2. **CSS Loading Issue**: Corrected stylesheet reference in HTML
3. **Module Import Paths**: Resolved Python module structure issues

## 🎯 Current Capabilities

### What Works (MVP Status)
✅ File upload and processing  
✅ Data structure detection  
✅ Natural language query processing  
✅ Variance analysis tool  
✅ LLM-powered response generation  
✅ WebSocket real-time communication  
✅ Session management  
✅ Error handling and retry logic  
✅ Responsive web interface  

### Tested Scenarios
- NVIDIA financial data variance analysis
- Multi-period comparison (2022-2025)
- Percentage and absolute variance calculations
- Significant change identification
- Natural language result formatting

## 🚧 Future Enhancement Opportunities

### Additional Analysis Tools
- Trend analysis and forecasting
- Ratio analysis (liquidity, profitability, efficiency)
- Peer comparison and benchmarking
- Cash flow analysis
- Growth rate calculations

### Data Visualization
- Interactive charts and graphs
- Trend visualization
- Comparative dashboards
- Export capabilities (PDF, Excel)

### Advanced Features
- Multi-file analysis
- Historical data management
- Automated report generation
- Email/notification system
- User authentication and multi-tenancy

### Performance Optimizations
- Caching layer for repeated queries
- Background processing for large datasets
- Database integration for data persistence
- API rate limiting and optimization

## 📁 Project Structure
```
analysis-agent/
├── app/
│   ├── api/           # WebSocket API handlers
│   ├── core/          # Core business logic
│   ├── llm/           # LLM provider implementations
│   └── tools/         # Analysis tool implementations
├── static/            # Frontend assets
├── temp/             # Temporary file storage
├── requirements.txt   # Python dependencies
└── README.md         # This documentation
```

## 🤝 Contributing

This is an active development project. Areas for contribution:
- Additional analysis tools
- New LLM provider integrations
- Frontend enhancements
- Performance optimizations
- Test coverage improvements

## 📄 License

MIT License - see LICENSE file for details

---

**Project Status**: MVP Complete ✅  
**Created**: July 15, 2025  
**Last Updated**: July 15, 2025  
**Author**: @fdemirciler