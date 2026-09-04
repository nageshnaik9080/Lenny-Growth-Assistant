from app.providers.cloud_provider import AnthropicProvider, OpenAIProvider
from app.providers.ollama_provider import OllamaProvider
from app.providers.cloud_provider import get_provider


def test_provider_factory_defaults(monkeypatch):
    assert isinstance(get_provider("ollama"), OllamaProvider)


def test_provider_factory_switches():
    assert isinstance(get_provider("anthropic"), AnthropicProvider)
    assert isinstance(get_provider("openai"), OpenAIProvider)
