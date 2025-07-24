import json
import re
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential
from app.llm.provider import LLMProvider


class GeminiProvider(LLMProvider):
    """Gemini implementation of LLM Provider"""

    def __init__(self, **config):
        """
        Initialize Gemini provider

        Args:
            config: Configuration dict with keys:
                - api_key: Gemini API key
                - model: Model name (default: gemini-2.5-flash)
                - temperature: Generation temperature (default: 0.7)
                - max_tokens: Maximum tokens to generate (optional)
        """
        self.api_key = config.get("api_key")
        self.model_name = config.get("model", "gemini-2.5-flash")
        self.temperature = float(config.get("temperature", 0.1))
        self.max_tokens = config.get("max_tokens")

        # Configure Gemini
        genai.configure(api_key=self.api_key)

        # Set up generation config
        generation_config = {}
        if self.temperature is not None:
            generation_config["temperature"] = self.temperature
        if self.max_tokens is not None:
            generation_config["max_output_tokens"] = self.max_tokens

        # Initialize model
        self.model = genai.GenerativeModel(
            model_name=self.model_name, generation_config=generation_config
        )

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    async def generate_text(self, prompt: str) -> str:
        """Generate text from prompt with retry logic"""
        response = self.model.generate_content(prompt)
        return response.text

    async def process_query(
        self,
        query: str,
        data_profile: Dict[str, Any],
        available_tools: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Process user query to determine which tool to use and with what parameters"""

        # Format conversation history
        formatted_history = ""
        if conversation_history:
            for message in conversation_history[
                -5:
            ]:  # Just use last 5 messages for context
                role = message["role"]
                content = message["content"]
                formatted_history += f"{role.upper()}: {content}\n\n"

        # Create a prompt that includes dataset information and available tools
        prompt = f"""
        You are a financial analysis assistant. Your task is to analyze a financial dataset based on the user's query.

        DATASET INFORMATION:
        File name: {data_profile.get('file_name')}
        Format: {data_profile.get('format')}
        Time periods available: {', '.join(data_profile.get('periods', []))}
        
        Sample data:
        {json.dumps(data_profile.get('sample_data', [])[:2], indent=2)}
        
        AVAILABLE TOOLS:
        {json.dumps(available_tools, indent=2)}
        
        CONVERSATION HISTORY:
        {formatted_history}
        
        USER QUERY: {query}
        
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

        # Generate response
        response_text = await self.generate_text(prompt)

        # Extract JSON
        tool_selection = self.extract_json(response_text)

        return tool_selection

    async def format_response(
        self, query: str, tool_result: Dict[str, Any], data_profile: Dict[str, Any]
    ) -> str:
        """Format tool results into a natural language response"""

        prompt = f"""
        You are a financial analyst assistant. You need to translate technical analysis results into a clear, business-focused explanation.
        
        USER QUERY: {query}
        
        ANALYSIS RESULTS:
        {json.dumps(tool_result, indent=2)}
        
        Based on these results, provide a comprehensive, easy-to-understand summary using Markdown.
        - Use headings, subheadings, and bullet points to structure the information.
        - Use bold and italics to emphasize key terms and findings.
        - **Crucially, format any tabular data using Markdown table syntax.**
        
        Your response should be well-structured, professional, and directly answer the user's query.
        Focus on the insights from the data, not the methodology.
        """

        response = await self.generate_text(prompt)
        return response

    def extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from text response"""
        try:
            # Find JSON content between code blocks
            json_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
            match = re.search(json_pattern, text)

            if match:
                json_str = match.group(1)
            else:
                # Try to extract JSON without markers
                json_pattern = r"({[\s\S]*})"
                match = re.search(json_pattern, text)
                if match:
                    json_str = match.group(1)
                else:
                    json_str = text

            return json.loads(json_str)
        except Exception as e:
            raise ValueError(f"Failed to parse JSON from LLM response: {str(e)}")
