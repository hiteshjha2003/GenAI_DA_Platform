from typing import Dict, List, Any, Optional
from utils.logger import logger

class PromptEngine:
    """Handles prompt templates and engineering for different tasks."""

    def __init__(self, schema_info: Optional[Dict[str, Any]] = None):
        self.schema_info = schema_info or {}

    def update_schema_info(self, schema_info: Dict[str, Any]):
        """Update schema information for context-aware prompting."""
        self.schema_info = schema_info

    def generate_sql_prompt(self, natural_query: str, table_name: Optional[str] = None) -> str:
        """Generate prompt for SQL query generation."""
        schema_context = ""
        if self.schema_info:
            tables = self.schema_info.get('tables', [])
            if table_name and table_name in tables:
                columns = self.schema_info.get('columns', {}).get(table_name, [])
                schema_context = f"""
Database Schema for table '{table_name}':
Columns: {', '.join(columns)}
"""
            else:
                schema_context = f"""
Available tables: {', '.join(tables)}
"""

        prompt = f"""You are a SQL expert. Convert the following natural language query into a valid SQL query.

{schema_context}
Natural Language Query: "{natural_query}"

Instructions:
- Generate only the SQL query without any explanation
- Use proper SQL syntax
- If table name is not specified in the query, assume the most relevant table from the schema
- Use appropriate JOINs if needed
- Include WHERE clauses for filtering
- Use aggregate functions when appropriate (SUM, COUNT, AVG, etc.)

SQL Query:"""

        return prompt.strip()

    def generate_python_transform_prompt(self, natural_query: str, df_info: Optional[Dict[str, Any]] = None) -> str:
        """Generate prompt for Python data transformation code generation."""
        df_context = ""
        if df_info:
            columns = df_info.get('columns', [])
            dtypes = df_info.get('dtypes', {})
            df_context = f"""
DataFrame Information:
Columns: {', '.join(columns)}
Column Types: {', '.join([f'{col}: {dtype}' for col, dtype in dtypes.items()])}
"""

        prompt = f"""You are a Python pandas expert. Convert the following natural language request into Python code using pandas.

{df_context}
Natural Language Request: "{natural_query}"

Instructions:
- Generate only Python code that transforms the DataFrame 'df'
- Use pandas operations (filtering, grouping, aggregating, etc.)
- The result should be stored in variable 'df'
- Include necessary imports if needed
- Use best practices for data manipulation
- Handle edge cases appropriately

Python Code:"""

        return prompt.strip()

    def generate_visualization_prompt(self, natural_query: str, df_info: Optional[Dict[str, Any]] = None) -> str:
        """Generate prompt for visualization suggestions."""
        df_context = ""
        if df_info:
            columns = df_info.get('columns', [])
            numeric_cols = df_info.get('numeric_columns', [])
            categorical_cols = df_info.get('categorical_columns', [])
            df_context = f"""
DataFrame Information:
Columns: {', '.join(columns)}
Numeric Columns: {', '.join(numeric_cols)}
Categorical Columns: {', '.join(categorical_cols)}
"""

        prompt = f"""You are a data visualization expert. Suggest appropriate visualizations for the following request.

{df_context}
Request: "{natural_query}"

Instructions:
- Suggest 1-3 most appropriate chart types
- Specify which columns to use for x-axis, y-axis, color, size
- Explain why each visualization is suitable
- Consider the data types and relationships

Response format:
1. Chart Type: [type]
   - X-axis: [column]
   - Y-axis: [column]
   - Reason: [explanation]

Visualization Suggestions:"""

        return prompt.strip()

    def generate_data_insights_prompt(self, df_info: Optional[Dict[str, Any]] = None) -> str:
        """Generate prompt for automatic data insights."""
        df_context = ""
        if df_info:
            columns = df_info.get('columns', [])
            shape = df_info.get('shape', (0, 0))
            df_context = f"""
DataFrame Information:
Shape: {shape[0]} rows, {shape[1]} columns
Columns: {', '.join(columns)}
"""

        prompt = f"""You are a data analyst. Analyze the following dataset and provide key insights.

{df_context}
Dataset Sample: [DataFrame content will be provided separately]

Instructions:
- Identify key patterns and trends
- Point out anomalies or interesting findings
- Suggest potential areas for further analysis
- Provide actionable insights
- Keep the analysis concise but comprehensive

Key Insights:"""

        return prompt.strip()

    def get_prompt_templates(self) -> Dict[str, str]:
        """Get all available prompt templates."""
        return {
            'sql_generation': self.generate_sql_prompt(""),
            'python_transform': self.generate_python_transform_prompt(""),
            'visualization': self.generate_visualization_prompt(""),
            'data_insights': self.generate_data_insights_prompt()
        }