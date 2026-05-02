import pandas as pd
from typing import Optional, Dict, Any, List
import streamlit as st
from utils.file_utils import FileProcessor
from core.db_manager import DatabaseManager
from utils.logger import logger

class DataLoader:
    """Handles data ingestion from various sources."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.uploaded_data: Optional[pd.DataFrame] = None
        self.data_metadata: Dict[str, Any] = {}

    def load_from_upload(self, uploaded_file) -> pd.DataFrame:
        """Load data from uploaded file."""
        try:
            self.uploaded_data = FileProcessor.process_uploaded_file(uploaded_file)
            self._extract_metadata()
            logger.info(f"Loaded data from uploaded file: {uploaded_file.name}")
            return self.uploaded_data
        except Exception as e:
            logger.error(f"Error loading uploaded file: {e}")
            raise

    def load_from_database(self, table_name: str) -> pd.DataFrame:
        """Load data from database table."""
        try:
            if not self.db_manager.is_connected():
                raise ConnectionError("Database not connected")

            query = f"SELECT * FROM {table_name}"
            self.uploaded_data = self.db_manager.execute_query(query)
            self._extract_metadata()
            logger.info(f"Loaded data from database table: {table_name}")
            return self.uploaded_data
        except Exception as e:
            logger.error(f"Error loading from database table {table_name}: {e}")
            raise

    def upload_to_database(self, table_name: str, if_exists: str = 'replace'):
        """Upload current data to database."""
        if self.uploaded_data is None:
            raise ValueError("No data loaded to upload")

        try:
            self.db_manager.upload_dataframe(self.uploaded_data, table_name, if_exists)
            logger.info(f"Uploaded data to database table: {table_name}")
        except Exception as e:
            logger.error(f"Error uploading to database: {e}")
            raise

    def clean_data(self, remove_nulls: bool = True, remove_duplicates: bool = True) -> pd.DataFrame:
        """Clean the loaded data."""
        if self.uploaded_data is None:
            raise ValueError("No data loaded to clean")

        try:
            cleaned_df = self.uploaded_data.copy()

            if remove_nulls:
                cleaned_df = cleaned_df.dropna()

            if remove_duplicates:
                cleaned_df = cleaned_df.drop_duplicates()

            self.uploaded_data = cleaned_df
            self._extract_metadata()
            logger.info("Data cleaned successfully")
            return cleaned_df
        except Exception as e:
            logger.error(f"Error cleaning data: {e}")
            raise

    def get_data_quality_report(self) -> Dict[str, Any]:
        """Generate data quality report."""
        if self.uploaded_data is None:
            raise ValueError("No data loaded")

        try:
            report = {
                'shape': self.uploaded_data.shape,
                'columns': list(self.uploaded_data.columns),
                'dtypes': self.uploaded_data.dtypes.to_dict(),
                'null_counts': self.uploaded_data.isnull().sum().to_dict(),
                'duplicate_count': self.uploaded_data.duplicated().sum(),
                'memory_usage': self.uploaded_data.memory_usage(deep=True).sum()
            }
            return report
        except Exception as e:
            logger.error(f"Error generating quality report: {e}")
            raise

    def _extract_metadata(self):
        """Extract metadata from loaded data."""
        if self.uploaded_data is not None:
            self.data_metadata = {
                'rows': len(self.uploaded_data),
                'columns': len(self.uploaded_data.columns),
                'column_names': list(self.uploaded_data.columns),
                'dtypes': self.uploaded_data.dtypes.to_dict(),
                'has_nulls': self.uploaded_data.isnull().any().any(),
                'duplicate_count': self.uploaded_data.duplicated().sum()
            }

    def get_metadata(self) -> Dict[str, Any]:
        """Get current data metadata."""
        return self.data_metadata

    def get_sample_data(self, n: int = 5) -> pd.DataFrame:
        """Get sample of loaded data."""
        if self.uploaded_data is None:
            raise ValueError("No data loaded")
        return self.uploaded_data.head(n)