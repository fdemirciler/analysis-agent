import pandas as pd
import re
from typing import Dict, Any, List, Optional, Tuple
from app.tools.preprocess import DataPreprocessor

class DataProfiler:
    """Extracts metadata from financial datasets"""
    
    def __init__(self):
        self.preprocessor = DataPreprocessor()
    
    def profile(self, df: pd.DataFrame, file_name: str) -> Dict[str, Any]:
        """
        Extract key metadata from dataframe
        
        Args:
            df: Raw dataframe
            file_name: Original filename
            
        Returns:
            dict: Contains column information, statistics, identified periods
        """
        # Preprocess data
        clean_df = self.preprocessor.preprocess(df)
        
        # Detect format (wide vs long)
        is_wide_format = self._detect_format(clean_df)
        
        # Get basic dataset stats
        basic_stats = {
            "file_name": file_name,
            "row_count": len(clean_df),
            "column_count": len(clean_df.columns),
            "format": "wide" if is_wide_format else "long"
        }
        
        # Identify periods and metrics
        periods, metrics = self._identify_periods_and_metrics(clean_df, is_wide_format)
        
        # Get column info
        columns_info = self._get_column_info(clean_df)
        
        # Combine into profile
        profile = {
            **basic_stats,
            "periods": periods,
            "metrics": metrics,
            "columns": columns_info,
            "sample_data": clean_df.head(3).to_dict('records')
        }
        
        return profile
    
    def _detect_format(self, df: pd.DataFrame) -> bool:
        """Detect if data is in wide format (periods as columns)"""
        # Check column names for years
        year_pattern = r'(19|20)\d{2}'  # Pattern for years (1900-2099)
        columns_with_years = [col for col in df.columns if isinstance(col, str) and re.search(year_pattern, str(col))]
        
        # If multiple columns contain years, likely wide format
        if len(columns_with_years) > 1:
            return True
            
        # Default to wide format for financial statements
        return True
    
    def _identify_periods_and_metrics(self, df: pd.DataFrame, is_wide_format: bool) -> Tuple[List[str], List[str]]:
        """Identify time periods and metrics in the dataset"""
        if is_wide_format:
            # Wide format: periods are columns, metrics are in first column
            metric_col = df.columns[0]
            metrics = df[metric_col].tolist() if metric_col in df else []
            
            # Remaining columns are periods
            periods = [str(col) for col in df.columns[1:]]
        else:
            # Long format: first column likely contains periods
            period_col = df.columns[0]
            periods = df[period_col].unique().tolist() if period_col in df else []
            
            # Remaining columns are metrics
            metrics = [col for col in df.columns[1:]]
            
        return periods, metrics
    
    def _get_column_info(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Get information about each column"""
        columns_info = []
        
        for col in df.columns:
            # Skip first column if it contains metrics
            if col == df.columns[0] and not pd.api.types.is_numeric_dtype(df[col]):
                columns_info.append({
                    "name": col,
                    "type": "category",
                    "unique_values": len(df[col].unique()),
                    "sample_values": df[col].dropna().unique()[:5].tolist()
                })
                continue
                
            # For numeric columns, get statistics
            if pd.api.types.is_numeric_dtype(df[col]):
                columns_info.append({
                    "name": col,
                    "type": "numeric",
                    "min": float(df[col].min()) if not pd.isna(df[col].min()) else None,
                    "max": float(df[col].max()) if not pd.isna(df[col].max()) else None,
                    "mean": float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
                    "null_count": int(df[col].isna().sum())
                })
            else:
                # For non-numeric columns
                columns_info.append({
                    "name": col,
                    "type": "text",
                    "unique_values": len(df[col].unique()),
                    "sample_values": df[col].dropna().unique()[:5].tolist()
                })
                
        return columns_info