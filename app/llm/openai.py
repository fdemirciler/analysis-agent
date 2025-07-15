import json
import re
from typing import Dict, Any, List, Optional
import openai
from tenacity import retry, stop_after_attempt, wait_exponential
from app.llm.provider import LLMProvider

class OpenaiProvider(LLMProvider):
    """OpenAI implementation of LLM Provider"""
    
    def __init__(self, **config):
        """
        Initialize OpenAI provider
        
        Args:
            config: Configuration dict with keys:
                - api_key: OpenAI API key
                - model: Model name (default: gpt-4o)
                - api_url: API base URL (optional)
                - temperature: Generation temperature (default: 0.7)
                - max_tokens: Maximum tokens to generate (default: 4096)
        """
        self.api_key = config.get("api_key")
        self.model_name = config.get("model", "gpt-4o")
        self.api_url = config.get("api_url")
        self.temperature = float(config.get("temperature", 0.7))
        self.max_tokens = int(config.get("max_tokens", 4096))
        
        # Configure OpenAI client
        client_params = {"api_key": self.api_key}
        if self.api_url:
            client_params["base_url"] = self.api_url
            
        self.client = openai.AsyncOpenAI(**client_params)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def generate_text(self, prompt: str) -> str:
        """Generate text from prompt with retry logic"""
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        return response.choices[0].message.content
    
    async def process_query(
        self, 
        query: str, 
        data_profile: Dict[str, Any],
        available_tools: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Process user query to determine which tool to use and with what parameters"""
        
        # Format conversation history
        messages = []
        if conversation_history:
            for message in conversation_history[-5:]:  # Just use last 5 messages for context
                messages.append({
                    "role": message["role"],
                    "content": message["content"]
                })
        
        # Create system message with dataset information and available tools
        system_message = f"""
        You are a financial analysis assistant. Your task is to analyze a financial dataset based on the user's query.

        DATASET INFORMATION:
        File name: {data_profile.get('file_name')}
        Format: {data_profile.get('format')}
        Time periods available: {', '.join(data_profile.get('periods', []))}
        
        Sample data:
        {json.dumps(data_profile.get('sample_data', [])[:2], indent=2)}
        
        AVAILABLE TOOLS:
        {json.dumps(available_tools, indent=2)}
        
        Based on the user's query, determine which tool to use and what parameters to pass to it.
        Return a JSON object with the following structure:
        {{
            "tool_name": "name of the tool to use",
            "parameters": {{
                // parameters specific to the chosen tool
            }},
            "reasoning": "explanation of why you chose this tool and these parameters"
        }}
        """
        
        # Prepare messages
        api_messages = [{"role": "system", "content": system_message}]
        api_messages.extend(messages)
        api_messages.append({"role": "user", "content": query})
        
        # Call OpenAI API
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=api_messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        response_text = response.choices[0].message.content
        
        # Extract JSON
        tool_selection = self.extract_json(response_text)
        
        return tool_selection
    
    async def format_response(
        self,
        query: str,
        tool_result: Dict[str, Any],
        data_profile: Dict[str, Any]
    ) -> str:
        """Format tool results into a natural language response"""
        
        system_message = """
        You are a financial analyst assistant. You need to translate technical analysis results into a clear, business-focused explanation.
        
        Provide a concise but informative response that:
        1. Directly answers the user's question
        2. Highlights the most significant findings and patterns
        3. Focuses on results rather than methodology
        4. Uses appropriate financial terminology
        5. Is written in a professional tone

        Your response should be well-structured with paragraphs and bullet points where appropriate.
        """
        
        user_message = f"""
        USER QUERY: {query}
        
        ANALYSIS RESULTS:
        {json.dumps(tool_result, indent=2)}
        """
        
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        return response.choices[0].message.content
    
    def extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from text response"""
        try:
            # Find JSON content between code blocks
            json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
            match = re.search(json_pattern, text)
            
            if match:
                json_str = match.group(1)
            else:
                # Try to extract JSON without markers
                json_pattern = r'({[\s\S]*})'
                match = re.search(json_pattern, text)
                if match:
                    json_str = match.group(1)
                else:
                    json_str = text
            
            return json.loads(json_str)
        except Exception as e:
            raise ValueError(f"Failed to parse JSON from LLM response: {str(e)}")