import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Configuration settings for the application."""

    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    # Database Settings
    DB_SERVERNAME = os.getenv("DB_SERVERNAME", "localhost")
    DB_DATABASE = os.getenv("DB_DATABASE")

    # LLM Configuration
    DEFAULT_LLM_PROVIDER = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

    # Supported file types
    SUPPORTED_FILE_TYPES = ['csv', 'xlsx', 'xls', 'txt', 'pdf', 'docx']

# Global settings instance
settings = Settings()