from typing import Optional

from .openai import OpenAIClient
from .claude import ClaudeClient
from .gemini import GeminiClient
from .grok import GrokClient
from .deepseek import DeepSeekClient
from ..base.interfaces import BaseLLM

PROVIDERS = {
    "openai": OpenAIClient,
    "claude": ClaudeClient,
    "gemini": GeminiClient,
    "grok": GrokClient,
    "deepseek": DeepSeekClient,
}

def get_provider(name: str, model_name: str, api_key: Optional[str] = None, **kwargs) -> BaseLLM:
    provider_class = PROVIDERS.get(name.lower())
    if not provider_class:
        raise ValueError(f"Unsupported provider: {name}")
    return provider_class(model_name, api_key, **kwargs)