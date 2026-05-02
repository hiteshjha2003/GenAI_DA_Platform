import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from utils.logger import logger

class DataProcessor:
    """Handles data processing and transformations."""

    def __init__(self, data_loader):
        self.data_loader = data_loader

    def execute_python_transformation(self, code: str) -> pd.DataFrame:
        """Execute Python code transformation on the data."""
        if self.data_loader.uploaded_data is None:
            raise ValueError("No data loaded for transformation")

        try:
            # Create a safe execution environment
            local_vars = {'df': self.data_loader.uploaded_data.copy(), 'pd': pd, 'np': np}
            global_vars = {'pd': pd, 'np': np}

            # Execute the transformation code
            exec(code, global_vars, local_vars)

            # Get the transformed dataframe (assuming it's stored in 'df')
            if 'df' in local_vars:
                result_df = local_vars['df']
                self.data_loader.uploaded_data = result_df
                self.data_loader._extract_metadata()
                logger.info("Python transformation executed successfully")
                return result_df
            else:
                raise ValueError("Transformation code must assign result to variable 'df'")
        except Exception as e:
            logger.error(f"Error executing Python transformation: {e}")
            raise

    def get_column_statistics(self, column: str) -> Dict[str, Any]:
        """Get statistics for a specific column."""
        if self.data_loader.uploaded_data is None:
            raise ValueError("No data loaded")

        if column not in self.data_loader.uploaded_data.columns:
            raise ValueError(f"Column '{column}' not found")

        try:
            col_data = self.data_loader.uploaded_data[column]
            stats = {
                'count': col_data.count(),
                'null_count': col_data.isnull().sum(),
                'unique_count': col_data.nunique(),
                'dtype': str(col_data.dtype)
            }

            if pd.api.types.is_numeric_dtype(col_data):
                stats.update({
                    'mean': col_data.mean(),
                    'median': col_data.median(),
                    'std': col_data.std(),
                    'min': col_data.min(),
                    'max': col_data.max(),
                    'quartiles': col_data.quantile([0.25, 0.5, 0.75]).to_dict()
                })
            elif pd.api.types.is_string_dtype(col_data):
                stats.update({
                    'most_common': col_data.mode().tolist() if not col_data.mode().empty else [],
                    'avg_length': col_data.str.len().mean() if col_data.notna().any() else 0
                })

            return stats
        except Exception as e:
            logger.error(f"Error getting column statistics for {column}: {e}")
            raise

    def filter_data(self, conditions: Dict[str, Any]) -> pd.DataFrame:
        """Filter data based on conditions."""
        if self.data_loader.uploaded_data is None:
            raise ValueError("No data loaded")

        try:
            df = self.data_loader.uploaded_data.copy()

            for column, condition in conditions.items():
                if column not in df.columns:
                    continue

                if isinstance(condition, dict):
                    if 'operator' in condition and 'value' in condition:
                        op = condition['operator']
                        val = condition['value']

                        if op == '==':
                            df = df[df[column] == val]
                        elif op == '!=':
                            df = df[df[column] != val]
                        elif op == '>':
                            df = df[df[column] > val]
                        elif op == '<':
                            df = df[df[column] < val]
                        elif op == '>=':
                            df = df[df[column] >= val]
                        elif op == '<=':
                            df = df[df[column] <= val]
                        elif op == 'contains':
                            df = df[df[column].str.contains(val, na=False)]
                        elif op == 'startswith':
                            df = df[df[column].str.startswith(val, na=False)]
                else:
                    # Simple equality filter
                    df = df[df[column] == condition]

            self.data_loader.uploaded_data = df
            self.data_loader._extract_metadata()
            logger.info("Data filtered successfully")
            return df
        except Exception as e:
            logger.error(f"Error filtering data: {e}")
            raise

    def aggregate_data(self, group_by: List[str], aggregations: Dict[str, str]) -> pd.DataFrame:
        """Aggregate data by grouping columns."""
        if self.data_loader.uploaded_data is None:
            raise ValueError("No data loaded")

        try:
            df = self.data_loader.uploaded_data.copy()

            # Map string aggregation functions to pandas functions
            agg_funcs = {
                'sum': 'sum',
                'mean': 'mean',
                'count': 'count',
                'min': 'min',
                'max': 'max',
                'std': 'std',
                'var': 'var'
            }

            agg_dict = {}
            for col, func in aggregations.items():
                if col in df.columns and func in agg_funcs:
                    agg_dict[col] = agg_funcs[func]

            if not agg_dict:
                raise ValueError("No valid aggregations specified")

            result = df.groupby(group_by).agg(agg_dict).reset_index()
            self.data_loader.uploaded_data = result
            self.data_loader._extract_metadata()
            logger.info("Data aggregated successfully")
            return result
        except Exception as e:
            logger.error(f"Error aggregating data: {e}")
            raise

    def sort_data(self, columns: List[str], ascending: bool = True) -> pd.DataFrame:
        """Sort data by specified columns."""
        if self.data_loader.uploaded_data is None:
            raise ValueError("No data loaded")

        try:
            df = self.data_loader.uploaded_data.copy()
            df = df.sort_values(columns, ascending=ascending)
            self.data_loader.uploaded_data = df
            logger.info("Data sorted successfully")
            return df
        except Exception as e:
            logger.error(f"Error sorting data: {e}")
            raise