from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import importlib
import os

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def generate_text(self, prompt: str) -> str:
        """Generate text from prompt"""
        pass
        
    @abstractmethod
    async def process_query(
        self, 
        query: str, 
        data_profile: Dict[str, Any],
        available_tools: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Process user query and determine tool parameters"""
        pass
    
    @abstractmethod
    async def format_response(
        self,
        query: str,
        tool_result: Dict[str, Any],
        data_profile: Dict[str, Any]
    ) -> str:
        """Format tool results into natural language response"""
        pass
        
    @abstractmethod
    def extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from text response"""
        pass

class LLMProviderFactory:
    """Factory for creating LLM providers"""
    
    @staticmethod
    def create_provider(config: Dict[str, Any] = None) -> LLMProvider:
        """
        Create an LLM provider based on configuration
        
        Args:
            config: Provider configuration. If None, will read from environment variables
            
        Returns:
            An initialized LLM provider
        """
        # Default to environment variables if no config provided
        if config is None:
            config = {
                "provider": os.getenv("LLM_PROVIDER", "gemini"),
                "api_key": os.getenv("LLM_API_KEY", ""),
                "model": os.getenv("LLM_MODEL", ""),
                "api_url": os.getenv("LLM_API_URL", ""),
                "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "8192")),
                "temperature": float(os.getenv("LLM_TEMPERATURE", "0.7"))
            }
        
        provider_type = config.get("provider", "gemini").lower()
        
        # Import the appropriate provider module
        try:
            provider_module = importlib.import_module(f"app.llm.{provider_type}")
            provider_class = getattr(provider_module, f"{provider_type.capitalize()}Provider")
            return provider_class(**config)
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Unsupported LLM provider: {provider_type}. Error: {str(e)}")