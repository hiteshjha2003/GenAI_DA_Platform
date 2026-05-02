import pandas as pd
import PyPDF2
from docx import Document
from pathlib import Path
from typing import Optional, Dict, Any
import io
from utils.logger import logger

class FileProcessor:
    """Handles file processing for various formats."""

    @staticmethod
    def read_csv(file_path: str) -> pd.DataFrame:
        """Read CSV file."""
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            logger.error(f"Error reading CSV file {file_path}: {e}")
            raise

    @staticmethod
    def read_excel(file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """Read Excel file."""
        try:
            return pd.read_excel(file_path, sheet_name=sheet_name)
        except Exception as e:
            logger.error(f"Error reading Excel file {file_path}: {e}")
            raise

    @staticmethod
    def read_text(file_path: str) -> str:
        """Read text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading text file {file_path}: {e}")
            raise

    @staticmethod
    def read_pdf(file_path: str) -> str:
        """Read PDF file."""
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            logger.error(f"Error reading PDF file {file_path}: {e}")
            raise

    @staticmethod
    def read_docx(file_path: str) -> str:
        """Read DOCX file."""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error reading DOCX file {file_path}: {e}")
            raise

    @staticmethod
    def process_uploaded_file(uploaded_file) -> pd.DataFrame:
        """Process uploaded file from Streamlit."""
        file_extension = Path(uploaded_file.name).suffix.lower()

        if file_extension == '.csv':
            return pd.read_csv(uploaded_file)
        elif file_extension in ['.xlsx', '.xls']:
            return pd.read_excel(uploaded_file)
        elif file_extension == '.txt':
            # For text files, we'll create a simple DataFrame with the content
            content = uploaded_file.read().decode('utf-8')
            return pd.DataFrame({'content': [content]})
        elif file_extension == '.pdf':
            # For PDF, extract text and create DataFrame
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return pd.DataFrame({'content': [text]})
        elif file_extension == '.docx':
            # For DOCX, extract text and create DataFrame
            doc = Document(io.BytesIO(uploaded_file.read()))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return pd.DataFrame({'content': [text]})
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

    @staticmethod
    def get_file_metadata(file_path: str) -> Dict[str, Any]:
        """Get metadata about a file."""
        path = Path(file_path)
        return {
            'name': path.name,
            'size': path.stat().st_size,
            'extension': path.suffix,
            'modified': path.stat().st_mtime
        }