# Financial Analysis Agent

An agentic AI workflow for financial data analysis built by @fdemirciler.

## Overview

This application allows users to upload financial data (CSV/Excel) and analyze it through natural language queries. The system uses an LLM to interpret queries, then routes them to specialized analysis tools.

## Features

- Upload CSV or Excel files containing financial data
- Chat interface for natural language queries
- Variance analysis between time periods
- Support for different LLM providers (Gemini, OpenAI)
- Real-time interaction via WebSockets

## Setup

1. Clone this repository
2. Copy `.env.example` to `.env` and add your API keys
3. Install dependencies: `pip install -r requirements.txt`
4. Run the application: `python -m app.main`
5. Open http://localhost:8000 in your browser

## Example Queries

- "Compare revenue between 2023 and 2024"
- "Analyze the variance in operating expenses between the last two years"
- "What metrics showed the largest percentage increase?"

## Architecture

- **Frontend**: HTML, CSS, JavaScript with WebSocket connection
- **Backend**: FastAPI, Pandas, LangGraph
- **LLM Integration**: Flexible provider system supporting Gemini and OpenAI

## License

MIT

Created on: 2025-07-15