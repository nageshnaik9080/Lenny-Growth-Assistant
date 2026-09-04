import json
import httpx
from collections.abc import AsyncGenerator
from app.config import get_settings
from .base import BaseLLMProvider
from .ollama_provider import OllamaProvider

class AnthropicProvider(BaseLLMProvider):
    name = "anthropic"

    def __init__(self):
        s = get_settings()
        self.api_key = s.anthropic_api_key
        self.model = s.anthropic_model

    async def generate_response(self, messages, system_prompt, temperature=0.3) -> AsyncGenerator[str, None]:
        if not self.api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not configured")
        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "temperature": temperature,
            "system": system_prompt,
            "messages": messages,
            "stream": True,
        }
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=10.0)) as client:
            async with client.stream("POST", "https://api.anthropic.com/v1/messages", headers=headers, json=payload) as response:
                if response.status_code >= 400:
                    body = await response.aread()
                    raise RuntimeError(f"Anthropic error {response.status_code}: {body.decode(errors='ignore')[:500]}")
                async for line in response.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    raw = line[5:].strip()
                    if raw == "[DONE]":
                        break
                    data = json.loads(raw)
                    if data.get("type") == "content_block_delta":
                        delta = data.get("delta", {})
                        if delta.get("type") == "text_delta" and delta.get("text"):
                            yield delta["text"]

    async def health(self) -> bool:
        return bool(self.api_key)


class OpenAIProvider(BaseLLMProvider):
    name = "openai"

    def __init__(self):
        s = get_settings()
        self.api_key = s.openai_api_key
        self.model = s.openai_model

    async def generate_response(self, messages, system_prompt, temperature=0.3) -> AsyncGenerator[str, None]:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        payload = {
            "model": self.model,
            "temperature": temperature,
            "stream": True,
            "messages": [{"role": "system", "content": system_prompt}, *messages],
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=10.0)) as client:
            async with client.stream("POST", "https://api.openai.com/v1/chat/completions", headers=headers, json=payload) as response:
                if response.status_code >= 400:
                    body = await response.aread()
                    raise RuntimeError(f"OpenAI error {response.status_code}: {body.decode(errors='ignore')[:500]}")
                async for line in response.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    raw = line[5:].strip()
                    if raw == "[DONE]":
                        break
                    data = json.loads(raw)
                    choices = data.get("choices", [])
                    if choices:
                        delta = choices[0].get("delta", {})
                        if delta.get("content"):
                            yield delta["content"]

    async def health(self) -> bool:
        return bool(self.api_key)


def get_provider(name: str | None = None) -> BaseLLMProvider:
    s = get_settings()
    selected = (name or s.default_llm_provider).lower()
    if selected == "ollama":
        return OllamaProvider()
    if selected == "anthropic":
        return AnthropicProvider()
    if selected == "openai":
        return OpenAIProvider()
    raise ValueError(f"Unsupported LLM provider: {selected}")
