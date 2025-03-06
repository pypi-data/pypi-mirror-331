from typing import Literal, Union, Optional, Dict
from llmfusion.providers import (
    OpenAIClient,
    ClaudeClient,
    GeminiClient,
    DeepSeekClient
)
from llmfusion.base.models import LLMInput, LLMConfig
from llmfusion.utils.key_manager import KeyManager

ProviderType = Literal["openai", "claude", "gemini", "deepseek"]


class LLMProvider:
    def __init__(self, provider: ProviderType, **kwargs):
        """Initialize the provider client once."""
        self.provider = provider
        self.key_manager = KeyManager(
            keys=kwargs.get("api_keys", []),  # Explicit keys (optional)
            env_file=kwargs.get("env_file", ".env"),  # Path to .env file (optional)
            cost_map_file=kwargs.get("cost_map_file", "cost_map.json")  # Path to cost map JSON (optional)
        )

        self.config = LLMConfig(
            api_key=None,  # Keys are managed by KeyManager
            key_manager=self.key_manager,  # Pass the KeyManager instance
            **kwargs
        )

        # Initialize the provider client
        self.client = self._get_client(provider, self.config)

    def _get_client(self, provider: ProviderType, config: LLMConfig):
        """Get the provider client with model validation."""
        if provider == "openai":
            return OpenAIClient(config)
        elif provider == "claude":
            return ClaudeClient(config)
        elif provider == "gemini":
            return GeminiClient(config)
        elif provider == "deepseek":
            return DeepSeekClient(config)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def get_completion(
            self,
            prompt: str,
            system_prompt: Optional[str] = None,
            read_cache: bool = True,
            **kwargs
    ) -> str:
        """Get completion from the provider.

        Args:
            prompt: The prompt text.
            system_prompt: Optional system prompt.
            read_cache: When False, bypasses the cache and forces a fresh API call.
            **kwargs: Additional parameters (e.g., temperature, max_tokens).

        Returns:
            Generated text completion.
        """
        input = LLMInput(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 1000)
        )
        return self.client.generate(input, read_cache=read_cache)

    async def aget_completion(
            self,
            prompt: str,
            system_prompt: Optional[str] = None,
            **kwargs
    ) -> str:
        """Async get completion from the provider."""
        input = LLMInput(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 1000)
        )
        return await self.client.agenerate(input)

    def get_embeddings(
            self,
            text: Union[str, list[str]],
            **kwargs
    ) -> Union[list[float], list[list[float]]]:
        """Get embeddings from the provider."""
        if isinstance(text, str):
            return self.client.embed(text)
        return [self.client.embed(t) for t in text]

    def get_usage_report(self) -> dict:
        """Get usage report for the provider."""
        return self.key_manager.get_usage_report()
