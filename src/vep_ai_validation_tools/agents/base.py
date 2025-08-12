"""
Base configuration for AI agents.
"""

from openai import AsyncOpenAI
from pydantic_ai.models.openai import ModelSettings, OpenAIModel
from pydantic_ai.providers import Provider


class OllamaProvider(Provider[AsyncOpenAI]):
    """Custom provider for Ollama using OpenAI-compatible API"""

    def __init__(
        self, base_url: str = "http://localhost:11434/v1", api_key: str = "ollama"
    ):
        self._base_url = base_url
        self._client = AsyncOpenAI(base_url=base_url, api_key=api_key)

    @property
    def client(self) -> AsyncOpenAI:
        return self._client

    @property
    def name(self) -> str:
        return "ollama"

    @property
    def base_url(self) -> str:
        return self._base_url

    def model_profile(self, model_name: str):
        return None


def create_ollama_model(
    model_name: str = "llama3.2", temperature: float = 0.1, max_retries: int = 5
) -> OpenAIModel:
    """Create a standardized Ollama model configuration"""
    ollama_provider = OllamaProvider()
    return OpenAIModel(
        model_name=model_name,
        provider=ollama_provider,
        settings=ModelSettings(temperature=temperature, max_retries=max_retries),
    )
