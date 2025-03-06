# ----- claude.py -----
from anthropic import Anthropic, AsyncAnthropic
from anthropic import APIError as ClaudeAPIError
from anthropic import RateLimitError as ClaudeRateLimitError
from typing import Optional, AsyncGenerator, Generator

from llmfusion.base.interfaces import BaseLLM
from llmfusion.base.exceptions import RateLimitError, ProviderError, InputValidationError
from llmfusion.base.models import LLMConfig, LLMInput
from llmfusion.providers.configs.model_global_configs import GlobalModelConfig
from llmfusion.utils.diskcache_ import diskcache_memoize

class ClaudeClient(BaseLLM):
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self._client = Anthropic(api_key=config.api_key)
        self._async_client = AsyncAnthropic(api_key=config.api_key)
        self.model_spec = GlobalModelConfig().get_model_spec("anthropic", config.model_name)

    def _validate_input(self, input: LLMInput):
        """Validate input parameters before API calls."""
        if not isinstance(input.prompt, str) or not input.prompt.strip():
            raise InputValidationError("Prompt must be a non-empty string", field="prompt")

        if input.system_prompt and not isinstance(input.system_prompt, str):
            raise InputValidationError("System prompt must be a string or None", field="system_prompt")

        if input.max_tokens > self.model_spec["max_output_tokens"]:
            raise InputValidationError(
                f"Max tokens ({input.max_tokens}) exceeds model maximum ({self.model_spec['max_output_tokens']})",
                field="max_tokens"
            )

    def _generate_impl(self, input: LLMInput) -> str:
        """Core synchronous text generation logic without caching."""
        self._validate_input(input)
        try:
            message = self._client.messages.create(
                model=self.config.model_name,
                system=str(input.system_prompt) if input.system_prompt else None,
                messages=[{"role": "user", "content": str(input.prompt)}],
                temperature=input.temperature,
                max_tokens=min(input.max_tokens, self.model_spec["max_output_tokens"])
            )
            return message.content[0].text
        except ClaudeRateLimitError as e:
            raise RateLimitError(f"Claude rate limit: {e}") from e
        except ClaudeAPIError as e:
            raise ProviderError(f"Claude API error: {e}") from e

    @diskcache_memoize(expire_tag="get_completion", size_gib="large")
    def _generate_cached(self, input: LLMInput) -> str:
        """Cached version of the text generation logic."""
        return self._generate_impl(input)

    def generate(self, input: LLMInput, read_cache: bool = True) -> str:
        """
        Synchronous text generation with optional caching.

        Args:
            input: An instance of LLMInput containing the prompt and other settings.
            read_cache: When False, bypasses cache and makes a fresh API call.

        Returns:
            Generated text as a string.
        """
        if read_cache:
            return self._generate_cached(input)
        else:
            return self._generate_impl(input)

    async def agenerate(self, input: LLMInput) -> str:
        """Asynchronous text generation."""
        self._validate_input(input)
        try:
            message = await self._async_client.messages.create(
                model=self.config.model_name,
                system=str(input.system_prompt) if input.system_prompt else None,
                messages=[{"role": "user", "content": str(input.prompt)}],
                temperature=input.temperature,
                max_tokens=min(input.max_tokens, self.model_spec["max_output_tokens"])
            )
            return message.content[0].text
        except ClaudeRateLimitError as e:
            raise RateLimitError(f"Claude rate limit: {e}") from e
        except ClaudeAPIError as e:
            raise ProviderError(f"Claude API error: {e}") from e

    def stream(self, input: LLMInput) -> Generator[str, None, None]:
        """Stream text generation."""
        self._validate_input(input)
        try:
            with self._client.messages.stream(
                model=self.config.model_name,
                system=str(input.system_prompt) if input.system_prompt else None,
                messages=[{"role": "user", "content": str(input.prompt)}],
                temperature=input.temperature,
                max_tokens=min(input.max_tokens, self.model_spec["max_output_tokens"])
            ) as stream:
                for chunk in stream:
                    yield chunk.content[0].text
        except ClaudeRateLimitError as e:
            raise RateLimitError(f"Claude rate limit: {e}") from e
        except ClaudeAPIError as e:
            raise ProviderError(f"Claude API error: {e}") from e
