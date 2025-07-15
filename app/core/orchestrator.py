from typing import Dict, Any, List, Tuple
import pandas as pd
import os
import logging
from app.core.data_profiler import DataProfiler
from app.llm.provider import LLMProvider

class Orchestrator:
    """Coordinates the end-to-end analysis workflow"""
    
    def __init__(self, llm_provider: LLMProvider, data_profiler: DataProfiler, tools: List):
        self.llm_provider = llm_provider
        self.data_profiler = data_profiler
        self.tools = {tool.tool_name: tool for tool in tools}
        self.logger = logging.getLogger(__name__)
    
    async def process_file(self, file_path: str, file_name: str) -> Tuple[Dict[str, Any], pd.DataFrame]:
        """
        Process uploaded file and return profile and dataframe
        
        Returns:
            Tuple containing data profile and pandas dataframe
        """
        self.logger.info(f"Processing file: {file_name}")
        
        try:
            # Load the dataframe
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
            
            # Profile the data
            data_profile = self.data_profiler.profile(df, file_name)
                
            return data_profile, df
            
        except Exception as e:
            self.logger.error(f"Error processing file: {str(e)}")
            raise
    
    async def process_query(
        self, 
        query: str, 
        data_profile: Dict[str, Any], 
        dataframe: pd.DataFrame,
        conversation_history: List[Dict[str, Any]] = None
    ) -> str:
        """
        Process user query and return response
        """
        self.logger.info(f"Processing query: {query}")
        
        try:
            # Get tool selection from LLM
            tool_selection = await self.llm_provider.process_query(
                query, 
                data_profile,
                [tool.get_tool_definition() for tool in self.tools.values()],
                conversation_history
            )
            
            self.logger.info(f"Selected tool: {tool_selection['tool_name']}")
            
            # Execute selected tool
            tool_name = tool_selection["tool_name"]
            parameters = tool_selection["parameters"]
            
            if tool_name not in self.tools:
                raise ValueError(f"Tool '{tool_name}' not found")
            
            tool = self.tools[tool_name]
            params_model = tool.input_schema(**parameters)
            
            self.logger.info(f"Executing tool with parameters: {params_model}")
            result = tool.execute(dataframe, params_model)
            
            # Format response
            response = await self.llm_provider.format_response(
                query,
                result.dict(),
                data_profile
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            raise