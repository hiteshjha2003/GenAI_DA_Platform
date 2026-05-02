from typing import Optional, Dict, Any, List
from ai.llm_manager import LLMManager
from ai.prompt_engine import PromptEngine
from core.db_manager import DatabaseManager
from utils.logger import logger

class SQLGenerator:
    """Handles natural language to SQL conversion."""

    def __init__(self, llm_manager: LLMManager, db_manager: DatabaseManager):
        self.llm_manager = llm_manager
        self.db_manager = db_manager
        self.prompt_engine = PromptEngine()

    def update_schema_context(self, schema_info: Dict[str, Any]):
        """Update schema information for better SQL generation."""
        self.prompt_engine.update_schema_info(schema_info)

    def generate_sql(self, natural_query: str, table_name: Optional[str] = None) -> str:
        """Convert natural language query to SQL."""
        try:
            prompt = self.prompt_engine.generate_sql_prompt(natural_query, table_name)
            sql_query = self.llm_manager.generate_response(prompt)

            # Clean up the response (remove markdown formatting if present)
            sql_query = self._clean_sql_response(sql_query)

            logger.info(f"Generated SQL from: '{natural_query}' -> {sql_query}")
            return sql_query
        except Exception as e:
            logger.error(f"Error generating SQL: {e}")
            raise

    def validate_sql(self, sql_query: str) -> bool:
        """Validate SQL query syntax (basic validation)."""
        try:
            # Basic validation - check for common SQL keywords
            sql_lower = sql_query.lower().strip()

            # Must contain SELECT, FROM, etc.
            if not any(keyword in sql_lower for keyword in ['select', 'insert', 'update', 'delete']):
                return False

            # Should not contain dangerous operations
            dangerous_keywords = ['drop', 'truncate', 'alter', 'create']
            if any(keyword in sql_lower for keyword in dangerous_keywords):
                logger.warning(f"Potentially dangerous SQL detected: {sql_query}")
                return False

            return True
        except Exception as e:
            logger.error(f"Error validating SQL: {e}")
            return False

    def execute_generated_sql(self, natural_query: str, table_name: Optional[str] = None) -> Dict[str, Any]:
        """Generate and execute SQL query."""
        try:
            sql_query = self.generate_sql(natural_query, table_name)

            if not self.validate_sql(sql_query):
                raise ValueError("Generated SQL query failed validation")

            if not self.db_manager.is_connected():
                raise ConnectionError("Database not connected")

            result_df = self.db_manager.execute_query(sql_query)

            return {
                'query': sql_query,
                'results': result_df,
                'success': True
            }
        except Exception as e:
            logger.error(f"Error executing generated SQL: {e}")
            return {
                'query': sql_query if 'sql_query' in locals() else None,
                'error': str(e),
                'success': False
            }

    def get_query_suggestions(self, table_name: Optional[str] = None) -> List[str]:
        """Get suggested queries for a table."""
        if not table_name:
            return []

        suggestions = [
            f"Show me all records from {table_name}",
            f"Count total records in {table_name}",
            f"Show me the first 10 records from {table_name}",
            f"What are the column names in {table_name}?",
            f"Show me any null values in {table_name}"
        ]

        return suggestions

    def _clean_sql_response(self, response: str) -> str:
        """Clean up LLM response to extract SQL query."""
        # Remove markdown code blocks
        response = response.strip()
        if response.startswith('```sql'):
            response = response[6:]
        elif response.startswith('```'):
            response = response[3:]

        if response.endswith('```'):
            response = response[:-3]

        # Remove extra whitespace and semicolons
        response = response.strip()
        if response.endswith(';'):
            response = response[:-1]

        return response.strip()