from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
from app.tools.base import AnalysisTool

class VarianceAnalysisInput(BaseModel):
    """Input parameters for variance analysis"""
    compare_periods: List[str] = Field(..., description="Periods to compare (e.g. ['2023', '2024'])")
    metrics: Optional[List[str]] = Field(None, description="Specific metrics to analyze (if None, analyzes all)")
    significance_threshold: Optional[float] = Field(5.0, description="Percentage threshold for significant variance")

class VarianceAnalysisOutput(BaseModel):
    """Output from variance analysis"""
    period_comparison: Dict[str, Any]
    significant_changes: List[Dict[str, Any]]
    detailed_results: List[Dict[str, Any]]
    summary: Dict[str, Any]

class VarianceAnalysisTool(AnalysisTool[VarianceAnalysisInput, VarianceAnalysisOutput]):
    """Tool for analyzing variances between time periods in financial data"""
    
    tool_name = "variance_analysis"
    description = "Compares financial metrics between time periods and identifies significant variances"
    input_schema = VarianceAnalysisInput
    output_schema = VarianceAnalysisOutput
    
    def execute(self, data: pd.DataFrame, params: VarianceAnalysisInput) -> VarianceAnalysisOutput:
        """Execute variance analysis on the dataset"""
        # Extract parameters
        compare_periods = params.compare_periods
        metrics = params.metrics
        threshold = params.significance_threshold
        
        # Validate that we have the periods to compare
        if len(compare_periods) != 2:
            raise ValueError("Variance analysis requires exactly 2 periods to compare")
            
        for period in compare_periods:
            if period not in data.columns:
                raise ValueError(f"Period '{period}' not found in dataset")
        
        # Extract the metrics if first column contains them
        metric_col = data.columns[0]
        all_metrics = data[metric_col].tolist()
        
        # Filter metrics if specified
        target_metrics = metrics if metrics else all_metrics
        
        # Prepare result containers
        detailed_results = []
        significant_changes = []
        
        # Analyze each metric
        for metric in target_metrics:
            # Find the row for this metric
            metric_row = data[data[metric_col] == metric]
            if len(metric_row) == 0:
                continue
                
            # Get values for both periods
            try:
                val_1 = float(metric_row[compare_periods[0]].values[0])
                val_2 = float(metric_row[compare_periods[1]].values[0])
                
                # Calculate variance
                abs_var = val_2 - val_1
                pct_var = (abs_var / val_1 * 100) if val_1 != 0 else float('inf')
                
                result = {
                    "metric": metric,
                    "period_1": compare_periods[0],
                    "period_2": compare_periods[1],
                    "value_1": val_1,
                    "value_2": val_2,
                    "absolute_variance": abs_var,
                    "percentage_variance": pct_var,
                    "is_significant": abs(pct_var) >= threshold
                }
                
                detailed_results.append(result)
                
                if abs(pct_var) >= threshold:
                    significant_changes.append({
                        "metric": metric,
                        "from_value": val_1,
                        "to_value": val_2,
                        "absolute_change": abs_var,
                        "percentage_change": pct_var,
                        "direction": "increase" if pct_var > 0 else "decrease"
                    })
                    
            except (ValueError, TypeError, IndexError):
                # Skip metrics that can't be compared numerically
                continue
        
        # Sort significant changes by absolute percentage
        significant_changes = sorted(significant_changes, key=lambda x: abs(x["percentage_change"]), reverse=True)
        
        # Create summary
        summary = {
            "periods_compared": compare_periods,
            "total_metrics_analyzed": len(detailed_results),
            "significant_changes_count": len(significant_changes),
            "largest_increase": significant_changes[0] if significant_changes and significant_changes[0]["direction"] == "increase" else None,
            "largest_decrease": next((x for x in significant_changes if x["direction"] == "decrease"), None)
        }
        
        # Return structured results
        return VarianceAnalysisOutput(
            period_comparison={
                "periods": compare_periods,
                "metrics_analyzed": len(detailed_results)
            },
            significant_changes=significant_changes,
            detailed_results=detailed_results,
            summary=summary
        )