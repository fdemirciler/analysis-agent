"""
Financial Data Cleaner

A comprehensive module for cleaning and standardizing financial data formats.
Handles various numeric formats including currencies, percentages, fractions,
scientific notation, and accounting formats.

"""

import re
import pandas as pd
from fractions import Fraction
import numpy as np
import logging
from typing import Union, Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class FinancialDataCleanerError(Exception):
    """Custom exception for FinancialDataCleaner errors."""

    pass


class FinancialDataCleaner:
    """
    A comprehensive data cleaning class that handles various financial data formats
    and converts them to standardized numeric values.
    """

    def __init__(self):
        # Define patterns for different data formats
        self.patterns = {
            "currency": re.compile(r"^[\$£€¥₹][\d,]+\.?\d*$"),
            "negative_currency": re.compile(r"^\([\$£€¥₹][\d,]+\.?\d*\)$"),
            "percentage": re.compile(r"^-?[\d,]+\.?\d*%$"),
            "accounting_negative": re.compile(r"^\([\d,]+\.?\d*\)$"),
            "scientific": re.compile(r"^-?[\d.]+[eE][+-]?\d+$"),
            "fraction": re.compile(r"^\d+/\d+$"),
            "number_with_commas": re.compile(r"^-?[\d,]+\.?\d*$"),
            "simple_number": re.compile(r"^-?[\d.]+$"),
        }

        # Define missing value indicators
        self.missing_indicators = {
            "-",
            "N/A",
            "n/a",
            "NA",
            "na",
            "NULL",
            "null",
            "None",
            "none",
            "",
            " ",
            "NaN",
            "nan",
            "#N/A",
            "#VALUE!",
            "#REF!",
            "#DIV/0!",
            "#NAME?",
            "#NUM!",
            "#NULL!",
        }

    def clean_value(self, value: Union[str, int, float, None]) -> Optional[float]:
        """
        Clean a single value and convert it to a standardized numeric format.

        Args:
            value: The input value to clean

        Returns:
            Cleaned numeric value or None for missing values

        Raises:
            FinancialDataCleanerError: If value type is unsupported
        """
        try:
            # Handle None and NaN values
            if value is None or (isinstance(value, float) and np.isnan(value)):
                return None

            # Convert to string and strip whitespace
            str_value = str(value).strip()

            # Check for missing value indicators
            if str_value in self.missing_indicators:
                return None

            # Try to handle different formats in order of complexity

            # 1. Currency formats: $26,914 → 26914.0
            if self.patterns["currency"].match(str_value):
                return self._clean_currency(str_value)

            # 2. Negative currency in parentheses: ($1,500) → -1500.0
            if self.patterns["negative_currency"].match(str_value):
                return self._clean_negative_currency(str_value)

            # 3. Percentages: 125.9% → 1.259
            if self.patterns["percentage"].match(str_value):
                return self._clean_percentage(str_value)

            # 4. Accounting format negatives: (1,500) → -1500.0
            if self.patterns["accounting_negative"].match(str_value):
                return self._clean_accounting_negative(str_value)

            # 5. Scientific notation: 1.5e6 → 1500000.0
            if self.patterns["scientific"].match(str_value):
                return self._clean_scientific(str_value)

            # 6. Fractions: 3/4 → 0.75
            if self.patterns["fraction"].match(str_value):
                return self._clean_fraction(str_value)

            # 7. Numbers with commas: 9,439 → 9439.0
            if self.patterns["number_with_commas"].match(str_value):
                return self._clean_number_with_commas(str_value)

            # 8. Simple numbers: 123.45 → 123.45
            if self.patterns["simple_number"].match(str_value):
                return self._clean_simple_number(str_value)

            # 9. Try to extract numbers from mixed text (last resort)
            return self._extract_number_from_text(str_value)

        except Exception as error:
            logger.warning(f"Error cleaning value '{value}': {str(error)}")
            return None

    def _clean_currency(self, value: str) -> float:
        """Clean currency format: $26,914 → 26914.0"""
        try:
            # Remove currency symbol and commas
            cleaned = re.sub(r"[\$£€¥₹,]", "", value)
            return float(cleaned)
        except (ValueError, AttributeError) as error:
            raise FinancialDataCleanerError(
                f"Failed to clean currency value '{value}': {error}"
            )

    def _clean_negative_currency(self, value: str) -> float:
        """Clean negative currency format: ($1,500) → -1500.0"""
        # Remove parentheses, currency symbol, and commas, then make negative
        cleaned = re.sub(r"[\(\)$£€¥₹,]", "", value)
        return -float(cleaned)

    def _clean_percentage(self, value: str) -> float:
        """Clean percentage format: 125.9% → 1.259"""
        try:
            # Remove % sign and commas, then divide by 100
            cleaned = re.sub(r"[,%]", "", value)
            return float(cleaned) / 100.0
        except (ValueError, AttributeError) as error:
            raise FinancialDataCleanerError(
                f"Failed to clean percentage value '{value}': {error}"
            )

    def _clean_accounting_negative(self, value: str) -> float:
        """Clean accounting negative format: (1,500) → -1500.0"""
        try:
            # Remove parentheses and commas, then make negative
            cleaned = re.sub(r"[\(\),]", "", value)
            return -float(cleaned)
        except (ValueError, AttributeError) as error:
            raise FinancialDataCleanerError(
                f"Failed to clean accounting negative value '{value}': {error}"
            )

    def _clean_scientific(self, value: str) -> float:
        """Clean scientific notation: 1.5e6 → 1500000.0"""
        try:
            return float(value)
        except ValueError as error:
            raise FinancialDataCleanerError(
                f"Failed to clean scientific notation value '{value}': {error}"
            )

    def _clean_fraction(self, value: str) -> float:
        """Clean fraction format: 3/4 → 0.75"""
        try:
            fraction = Fraction(value)
            return float(fraction)
        except (ValueError, ZeroDivisionError) as error:
            raise FinancialDataCleanerError(
                f"Failed to clean fraction value '{value}': {error}"
            )

    def _clean_number_with_commas(self, value: str) -> float:
        """Clean number with commas: 9,439 → 9439.0"""
        try:
            cleaned = value.replace(",", "")
            return float(cleaned)
        except ValueError as error:
            raise FinancialDataCleanerError(
                f"Failed to clean number with commas '{value}': {error}"
            )

    def _clean_simple_number(self, value: str) -> float:
        """Clean simple number: 123.45 → 123.45"""
        try:
            return float(value)
        except ValueError as error:
            raise FinancialDataCleanerError(
                f"Failed to clean simple number '{value}': {error}"
            )

    def _extract_number_from_text(self, value: str) -> Optional[float]:
        """
        Last resort: try to extract a number from mixed text.
        This handles cases like "Revenue: $1,234" or "Growth 15.5%"
        """
        try:
            # Look for currency patterns first
            currency_match = re.search(r"[\$£€¥₹]([\d,]+\.?\d*)", value)
            if currency_match:
                return self._clean_currency(currency_match.group(0))

            # Look for percentage patterns
            percent_match = re.search(r"([\d,]+\.?\d*)%", value)
            if percent_match:
                return self._clean_percentage(percent_match.group(0))

            # Look for any number with commas
            number_match = re.search(r"([\d,]+\.?\d*)", value)
            if number_match:
                return self._clean_number_with_commas(number_match.group(1))

            # If nothing found, return None
            return None

        except (ValueError, AttributeError):
            return None

    def clean_dataframe(
        self, df: pd.DataFrame, exclude_columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Clean all numeric columns in a DataFrame.

        Args:
            df: Input DataFrame
            exclude_columns: List of column names to exclude from cleaning

        Returns:
            DataFrame with cleaned numeric values

        Raises:
            FinancialDataCleanerError: If DataFrame processing fails
        """
        if exclude_columns is None:
            exclude_columns = []

        if not isinstance(df, pd.DataFrame):
            raise FinancialDataCleanerError("Input must be a pandas DataFrame")

        try:
            df_cleaned = df.copy()

            for column in df_cleaned.columns:
                if column not in exclude_columns:
                    df_cleaned[column] = df_cleaned[column].apply(self.clean_value)

            logger.info(
                f"Successfully cleaned DataFrame with {len(df_cleaned.columns)} columns"
            )
            return df_cleaned

        except Exception as error:
            raise FinancialDataCleanerError(f"Failed to clean DataFrame: {error}")

    def analyze_formats(self, values: list) -> dict:
        """
        Analyze the formats present in a list of values.

        Args:
            values: List of values to analyze

        Returns:
            Dictionary with format counts and examples
        """
        format_analysis = {
            "currency": [],
            "percentage": [],
            "accounting_negative": [],
            "scientific": [],
            "fraction": [],
            "number_with_commas": [],
            "simple_number": [],
            "missing_values": [],
            "unrecognized": [],
        }

        for value in values:
            if value is None:
                format_analysis["missing_values"].append(value)
                continue

            str_value = str(value).strip()

            if str_value in self.missing_indicators:
                format_analysis["missing_values"].append(str_value)
            elif self.patterns["currency"].match(str_value) or self.patterns[
                "negative_currency"
            ].match(str_value):
                format_analysis["currency"].append(str_value)
            elif self.patterns["percentage"].match(str_value):
                format_analysis["percentage"].append(str_value)
            elif self.patterns["accounting_negative"].match(str_value):
                format_analysis["accounting_negative"].append(str_value)
            elif self.patterns["scientific"].match(str_value):
                format_analysis["scientific"].append(str_value)
            elif self.patterns["fraction"].match(str_value):
                format_analysis["fraction"].append(str_value)
            elif self.patterns["number_with_commas"].match(str_value):
                format_analysis["number_with_commas"].append(str_value)
            elif self.patterns["simple_number"].match(str_value):
                format_analysis["simple_number"].append(str_value)
            else:
                format_analysis["unrecognized"].append(str_value)

        # Convert to summary with counts and examples
        summary = {}
        for format_type, examples in format_analysis.items():
            if examples:
                summary[format_type] = {
                    "count": len(examples),
                    "examples": examples[:5],  # Show first 5 examples
                }

        return summary


def clean_financial_value(value: Union[str, int, float, None]) -> Optional[float]:
    """
    Quick function to clean a single financial value.

    Args:
        value: The value to clean (string, number, or None)

    Returns:
        Cleaned numeric value or None for missing values
    """
    cleaner = FinancialDataCleaner()
    return cleaner.clean_value(value)


# Function to clean a list or series of values
def clean_financial_series(
    values: Union[List[Any], pd.Series],
) -> Union[List[Optional[float]], pd.Series]:
    """
    Clean a list or pandas Series of financial values.

    Args:
        values: List or Series of values to clean

    Returns:
        List of cleaned values or pandas Series
    """
    cleaner = FinancialDataCleaner()
    if isinstance(values, pd.Series):
        return values.apply(cleaner.clean_value)
    else:  # list or other iterable
        return [cleaner.clean_value(value) for value in values]
