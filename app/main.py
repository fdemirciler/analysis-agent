import os
import uvicorn
import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.api.websocket import WebSocketAPI
from app.core.session import SessionManager
from app.core.orchestrator import Orchestrator
from app.core.data_profiler import DataProfiler
from app.llm.provider import LLMProviderFactory
from app.tools.variance import VarianceAnalysisTool

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Set up FastAPI
app = FastAPI(title="Financial Data Analysis Agent")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
llm_provider = LLMProviderFactory.create_provider()  # Will read from environment variables
data_profiler = DataProfiler()

# Initialize tools
tools = [
    VarianceAnalysisTool(),
]

# Initialize orchestrator
orchestrator = Orchestrator(
    llm_provider=llm_provider,
    data_profiler=data_profiler,
    tools=tools
)

# Initialize session manager and WebSocket API
session_manager = SessionManager()
websocket_api = WebSocketAPI(app, orchestrator, session_manager)

# Serve static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(f"Starting Financial Data Analysis Agent on port {port}")
    logger.info(f"Using LLM Provider: {os.getenv('LLM_PROVIDER')} with model {os.getenv('LLM_MODEL')}")
    
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=debug)