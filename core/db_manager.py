from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from typing import Optional, List, Dict, Any
import pandas as pd
from config.settings import settings
from utils.logger import logger

class DatabaseManager:
    """Manages database connections and operations."""

    def __init__(self):
        self.engine: Optional[Engine] = None
        self.db_type: Optional[str] = None

    def connect_sqlserver(self, server: str, database: str) -> bool:
        """Connect to SQL Server database."""
        try:
            connection_string = f"mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
            self.engine = create_engine(connection_string)
            self.db_type = 'sqlserver'
            logger.info(f"Connected to SQL Server: {server}/{database}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to SQL Server: {e}")
            return False

    def disconnect(self):
        """Disconnect from database."""
        if self.engine:
            self.engine.dispose()
            self.engine = None
            self.db_type = None
            logger.info("Disconnected from database")

    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute SQL query and return results as DataFrame."""
        if not self.engine:
            raise ConnectionError("No database connection established")

        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                return pd.DataFrame(result.fetchall(), columns=result.keys())
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise

    def get_table_list(self) -> List[str]:
        """Get list of tables in the database."""
        if not self.engine:
            raise ConnectionError("No database connection established")

        try:
            if self.db_type == 'sqlserver':
                query = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'"
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")

            df = self.execute_query(query)
            return df.iloc[:, 0].tolist()
        except Exception as e:
            logger.error(f"Error getting table list: {e}")
            raise

    def get_table_schema(self, table_name: str) -> pd.DataFrame:
        """Get schema information for a table."""
        if not self.engine:
            raise ConnectionError("No database connection established")

        try:
            if self.db_type == 'sqlserver':
                query = f"SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'"
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")

            return self.execute_query(query)
        except Exception as e:
            logger.error(f"Error getting table schema for {table_name}: {e}")
            raise

    def upload_dataframe(self, df: pd.DataFrame, table_name: str, if_exists: str = 'replace'):
        """Upload DataFrame to database table."""
        if not self.engine:
            raise ConnectionError("No database connection established")

        try:
            df.to_sql(table_name, self.engine, if_exists=if_exists, index=False)
            logger.info(f"Uploaded DataFrame to table: {table_name}")
        except Exception as e:
            logger.error(f"Error uploading DataFrame to {table_name}: {e}")
            raise

    def is_connected(self) -> bool:
        """Check if database connection is active."""
        return self.engine is not None