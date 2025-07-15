import pandas as pd
import numpy as np
import re

class DataPreprocessor:
    """Handles cleaning and standardization of financial datasets"""
    
    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize financial data"""
        # Create a copy to avoid modifying the original
        clean_df = df.copy()
        
        # Handle index column if unnamed
        if clean_df.index.name is None and clean_df.index.dtype == 'object':
            clean_df = clean_df.reset_index()
            if 'index' in clean_df.columns:
                clean_df.rename(columns={'index': 'Metric'}, inplace=True)
                
        # Clean column names
        clean_df.columns = [str(col).strip() for col in clean_df.columns]
                
        # Convert data columns containing currency, percentages etc. to numeric
        for col in clean_df.columns:
            if col == 'Metric' or col == clean_df.columns[0]:
                continue
                
            clean_df[col] = self._convert_to_numeric(clean_df[col])
            
        return clean_df
    
    def _convert_to_numeric(self, series: pd.Series) -> pd.Series:
        """Convert string representations of numbers to actual numeric values"""
        
        def clean_value(val):
            if pd.isna(val) or val == '-':
                return np.nan
                
            if isinstance(val, (int, float)):
                return val
                
            # Remove currency symbols, commas and spaces
            if isinstance(val, str):
                # Handle percentages
                if '%' in val:
                    return float(re.sub(r'[^\d.-]', '', val)) / 100
                    
                # Handle currency and other formatted numbers
                val = re.sub(r'[^\d.-]', '', val)
                if val:
                    return float(val)
                    
            return np.nan
            
        return series.apply(clean_value)