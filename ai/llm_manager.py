from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import openai
import groq
import ollama
from config.settings import settings
from utils.logger import logger

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response from the LLM."""
        pass

class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider."""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        openai.api_key = api_key

    def generate_response(self, prompt: str, **kwargs) -> str:
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.7)
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

class GroqProvider(LLMProvider):
    """Groq LLM provider."""

    def __init__(self, api_key: str, model: str = "mixtral-8x7b-32768"):
        self.api_key = api_key
        self.model = model
        self.client = groq.Groq(api_key=api_key)

    def generate_response(self, prompt: str, **kwargs) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.7)
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise

class OllamaProvider(LLMProvider):
    """Ollama local LLM provider."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url
        self.model = model
        self.client = ollama.Client(host=base_url)

    def generate_response(self, prompt: str, **kwargs) -> str:
        try:
            response = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={
                    "temperature": kwargs.get('temperature', 0.7),
                    "num_predict": kwargs.get('max_tokens', 1000)
                }
            )
            return response['message']['content'].strip()
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise

class LLMManager:
    """Manages different LLM providers."""

    def __init__(self):
        self.providers = {}
        self.current_provider = None
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize available LLM providers."""
        # OpenAI
        if settings.OPENAI_API_KEY:
            self.providers['openai'] = OpenAIProvider(settings.OPENAI_API_KEY)

        # Groq
        if settings.GROQ_API_KEY:
            self.providers['groq'] = GroqProvider(settings.GROQ_API_KEY)

        # Ollama (always available if running locally)
        try:
            self.providers['ollama'] = OllamaProvider(
                base_url=settings.OLLAMA_BASE_URL,
                model=settings.OLLAMA_MODEL
            )
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")

        # Set default provider
        if settings.DEFAULT_LLM_PROVIDER in self.providers:
            self.current_provider = settings.DEFAULT_LLM_PROVIDER
        elif self.providers:
            self.current_provider = list(self.providers.keys())[0]

    def set_provider(self, provider_name: str):
        """Set the current LLM provider."""
        if provider_name not in self.providers:
            available = list(self.providers.keys())
            raise ValueError(f"Provider '{provider_name}' not available. Available: {available}")

        self.current_provider = provider_name
        logger.info(f"LLM provider set to: {provider_name}")

    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using current provider."""
        if not self.current_provider:
            raise ValueError("No LLM provider configured")

        provider = self.providers[self.current_provider]
        return provider.generate_response(prompt, **kwargs)

    def get_available_providers(self) -> list:
        """Get list of available providers."""
        return list(self.providers.keys())

    def get_current_provider(self) -> Optional[str]:
        """Get current provider name."""
        return self.current_provider