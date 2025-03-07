# ----- deepseek.py -----
import openai
from openai import APIConnectionError, APIError, RateLimitError as OpenAIRateLimitError
from typing import Optional, Generator, AsyncGenerator
from pydantic import Field

from llmfusion.base.interfaces import BaseLLM
from llmfusion.base.exceptions import RateLimitError, ProviderError, InputValidationError
from llmfusion.base.models import LLMConfig, LLMInput
from llmfusion.providers.configs.model_global_configs import GlobalModelConfig
from llmfusion.utils.diskcache_ import diskcache_memoize


class DeepSeekClient(BaseLLM):
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = openai.OpenAI(
            api_key=config.api_key,
            base_url="https://api.deepseek.com/v1"
        )
        self.async_client = openai.AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )
        self.model_spec = GlobalModelConfig().get_model_spec("deepseek", config.model_name)

    def _validate_input(self, input: LLMInput):
        """Validate input parameters"""
        if not isinstance(input.prompt, str) or not input.prompt.strip():
            raise InputValidationError("Prompt must be a non-empty string", field="prompt")

        if input.system_prompt and not isinstance(input.system_prompt, str):
            raise InputValidationError("System prompt must be a string or None", field="system_prompt")

        if input.max_tokens > self.model_spec["max_output_tokens"]:
            raise InputValidationError(
                f"Max tokens ({input.max_tokens}) exceeds model maximum ({self.model_spec['max_output_tokens']})",
                field="max_tokens"
            )

    def _build_messages(self, input: LLMInput) -> list[dict]:
        """Build messages list for API request"""
        messages = []
        if input.system_prompt:
            messages.append({"role": "system", "content": input.system_prompt})
        messages.append({"role": "user", "content": input.prompt})
        return messages

    def _uncached_generate(self, input: LLMInput) -> str:
        """Actual sync generation logic without caching"""
        self._validate_input(input)
        try:
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=self._build_messages(input),
                temperature=input.temperature,
                max_tokens=min(input.max_tokens, self.model_spec["max_output_tokens"])
            )
            return response.choices[0].message.content
        except OpenAIRateLimitError as e:
            raise RateLimitError(f"DeepSeek rate limit: {str(e)}") from e
        except (APIConnectionError, APIError) as e:
            raise ProviderError(f"DeepSeek API error: {str(e)}") from e

    @diskcache_memoize(expire_tag="deepseek_completion", size_gib="medium")
    def _generate_cached(self, input: LLMInput) -> str:
        """Cached version of generation logic"""
        return self._uncached_generate(input)

    def generate(self, input: LLMInput, read_cache: bool = True) -> str:
        """
        Generate text completion with optional caching.

        Args:
            input: An LLMInput instance containing the prompt and other settings.
            read_cache: When False, bypasses cache and makes a fresh API call.

        Returns:
            Generated text content as a string.
        """
        if read_cache:
            return self._generate_cached(input)
        else:
            return self._uncached_generate(input)

    async def agenerate(self, input: LLMInput) -> str:
        """Async generation"""
        return await self._uncached_agenerate(input)

    async def _uncached_agenerate(self, input: LLMInput) -> str:
        """Actual async generation logic without caching"""
        self._validate_input(input)
        try:
            response = await self.async_client.chat.completions.create(
                model=self.config.model_name,
                messages=self._build_messages(input),
                temperature=input.temperature,
                max_tokens=min(input.max_tokens, self.model_spec["max_output_tokens"])
            )
            return response.choices[0].message.content
        except OpenAIRateLimitError as e:
            raise RateLimitError(f"DeepSeek rate limit: {str(e)}") from e
        except (APIConnectionError, APIError) as e:
            raise ProviderError(f"DeepSeek API error: {str(e)}") from e

    def stream(self, input: LLMInput) -> Generator[str, None, None]:
        """Stream text generation"""
        self._validate_input(input)
        try:
            stream = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=self._build_messages(input),
                temperature=input.temperature,
                max_tokens=min(input.max_tokens, self.model_spec["max_output_tokens"]),
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except OpenAIRateLimitError as e:
            raise RateLimitError(f"DeepSeek rate limit: {str(e)}") from e
        except (APIConnectionError, APIError) as e:
            raise ProviderError(f"DeepSeek API error: {str(e)}") from e
