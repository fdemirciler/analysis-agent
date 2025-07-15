from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, TypeVar
from pydantic import BaseModel
import pandas as pd

# Generic type variables for input and output schemas
I = TypeVar('I', bound=BaseModel)
O = TypeVar('O', bound=BaseModel)

class AnalysisTool(Generic[I, O], ABC):
    """Base class for all analysis tools"""
    
    tool_name: str
    description: str
    input_schema: type[I]
    output_schema: type[O]
    
    @abstractmethod
    def execute(self, data: pd.DataFrame, params: I) -> O:
        """Execute the analysis on the provided data"""
        pass
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Return tool definition for LLM"""
        return {
            "name": self.tool_name,
            "description": self.description,
            "input_schema": self.input_schema.schema(),
            "output_schema": self.output_schema.schema()
        }