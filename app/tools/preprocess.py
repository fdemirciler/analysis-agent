import pandas as pd
import numpy as np
import logging
from app.tools.data_cleaner import FinancialDataCleaner

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Handles cleaning and standardization of financial datasets"""

    def __init__(self):
        self.cleaner = FinancialDataCleaner()

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize financial data"""
        # Create a copy to avoid modifying the original
        clean_df = df.copy()

        # Handle index column if unnamed
        if clean_df.index.name is None and clean_df.index.dtype == "object":
            clean_df = clean_df.reset_index()
            if "index" in clean_df.columns:
                clean_df.rename(columns={"index": "Metric"}, inplace=True)

        # Clean column names
        clean_df.columns = [str(col).strip() for col in clean_df.columns]

        # Determine which columns to exclude from cleaning (typically the first column with metrics)
        exclude_columns = []
        if len(clean_df.columns) > 0:
            first_col = clean_df.columns[0]
            if first_col == "Metric" or first_col.lower() in [
                "metric",
                "metrics",
                "account",
                "item",
            ]:
                exclude_columns.append(first_col)

        # Use FinancialDataCleaner to clean numeric columns
        try:
            cleaned_df = self.cleaner.clean_dataframe(
                clean_df, exclude_columns=exclude_columns
            )
            logger.info(
                f"Successfully preprocessed DataFrame with shape {cleaned_df.shape}"
            )
            return cleaned_df
        except Exception as e:
            logger.error(f"Error during data preprocessing: {str(e)}")
            # Fallback to original cleaning method if new cleaner fails
            return self._fallback_clean(clean_df, exclude_columns)

    def _fallback_clean(self, df: pd.DataFrame, exclude_columns: list) -> pd.DataFrame:
        """Fallback cleaning method using the original logic"""
        logger.warning("Using fallback cleaning method")
        clean_df = df.copy()

        for col in clean_df.columns:
            if col not in exclude_columns:
                clean_df[col] = self._convert_to_numeric_fallback(clean_df[col])

        return clean_df

    def _convert_to_numeric_fallback(self, series: pd.Series) -> pd.Series:
        """Original convert to numeric method as fallback"""
        import re

        def clean_value(val):
            if pd.isna(val) or val == "-":
                return np.nan

            if isinstance(val, (int, float)):
                return val

            # Remove currency symbols, commas and spaces
            if isinstance(val, str):
                # Handle percentages
                if "%" in val:
                    return float(re.sub(r"[^\d.-]", "", val)) / 100

                # Handle currency and other formatted numbers
                val = re.sub(r"[^\d.-]", "", val)
                if val:
                    return float(val)

            return np.nan

        return series.apply(clean_value)

    def analyze_data_formats(self, df: pd.DataFrame) -> dict:
        """Analyze the formats present in the DataFrame using FinancialDataCleaner"""
        format_summary = {}

        for col in df.columns:
            if col != "Metric" and col != df.columns[0]:
                values = df[col].dropna().tolist()
                if values:
                    format_summary[col] = self.cleaner.analyze_formats(values)

        return format_summary
