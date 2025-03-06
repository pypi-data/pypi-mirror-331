# ----- gemini.py -----
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from typing import Optional, AsyncGenerator, Generator
from pydantic import Field

from llmfusion.base.interfaces import BaseLLM
from llmfusion.base.exceptions import RateLimitError, ProviderError, InputValidationError
from llmfusion.base.models import LLMConfig, LLMInput
from llmfusion.providers.configs.model_global_configs import GlobalModelConfig
from llmfusion.utils.diskcache_ import diskcache_memoize


class GeminiConfig(LLMConfig):
    """Gemini-specific configuration model"""
    model_name: str = Field(default="gemini-pro", description="Gemini model name")
    safety_settings: Optional[dict] = Field(
        default=None,
        description="Safety settings for content generation"
    )


class GeminiClient(BaseLLM):
    def __init__(self, config: GeminiConfig):
        super().__init__(config)
        genai.configure(api_key=config.api_key)
        self.model = genai.GenerativeModel(config.model_name)
        self.model_spec = GlobalModelConfig().get_model_spec("google", config.model_name)

    def _validate_input(self, input: LLMInput):
        """Validate input against Gemini's requirements"""
        if not isinstance(input.prompt, str) or not input.prompt.strip():
            raise InputValidationError("Prompt must be a non-empty string", field="prompt")

        if input.system_prompt:
            raise InputValidationError("Gemini does not support system prompts", field="system_prompt")

        if input.max_tokens > self.model_spec["max_output_tokens"]:
            raise InputValidationError(
                f"Max tokens ({input.max_tokens}) exceeds model maximum ({self.model_spec['max_output_tokens']})",
                field="max_tokens"
            )

    def _format_prompt(self, prompt: str) -> list:
        """Format prompt according to Gemini's requirements"""
        return [{"role": "user", "parts": [prompt]}]

    def _create_generation_config(self, input: LLMInput) -> dict:
        """Create generation config from input parameters"""
        return {
            "temperature": input.temperature,
            "max_output_tokens": min(
                input.max_tokens,
                self.model_spec["max_output_tokens"]
            )
        }

    def _parse_response(self, response) -> str:
        """Extract text from Gemini response"""
        if not response.parts:
            raise ProviderError("No content in Gemini response")
        return " ".join(part.text for part in response.parts if hasattr(part, 'text'))

    def _uncached_generate(self, input: LLMInput) -> str:
        """Actual generation logic without caching"""
        self._validate_input(input)
        try:
            response = self.model.generate_content(
                contents=self._format_prompt(input.prompt),
                generation_config=self._create_generation_config(input),
            )
            return self._parse_response(response)
        except google_exceptions.TooManyRequests as e:
            raise RateLimitError(f"Gemini rate limit: {str(e)}") from e
        except google_exceptions.GoogleAPIError as e:
            raise ProviderError(f"Gemini API error: {str(e)}") from e

    @diskcache_memoize(expire_tag="get_completion", size_gib="medium")
    def _generate_cached(self, input: LLMInput) -> str:
        """Cached version of generation logic"""
        return self._uncached_generate(input)

    def generate(self, input: LLMInput, read_cache: bool = True) -> str:
        """
        Generate text completion with optional caching.

        Args:
            input: An LLMInput instance containing the prompt and other settings.
            read_cache: When False, bypasses the cache and makes a fresh API call.

        Returns:
            Generated text content as a string.
        """
        if read_cache:
            return self._generate_cached(input)
        else:
            return self._uncached_generate(input)

    async def agenerate(self, input: LLMInput) -> str:
        """Async generation (Gemini API currently doesn't support native async)"""
        return await self._async_fallback_generate(input)

    async def _async_fallback_generate(self, input: LLMInput) -> str:
        """Fallback async implementation using threads"""
        import asyncio
        from functools import partial
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            partial(self._uncached_generate, input)
        )

    def stream(self, input: LLMInput) -> Generator[str, None, None]:
        """Stream text generation"""
        self._validate_input(input)
        try:
            response = self.model.generate_content(
                contents=self._format_prompt(input.prompt),
                generation_config=self._create_generation_config(input),
                stream=True
            )
            for chunk in response:
                yield self._parse_response(chunk)
        except google_exceptions.TooManyRequests as e:
            raise RateLimitError(f"Gemini rate limit: {str(e)}") from e
        except google_exceptions.GoogleAPIError as e:
            raise ProviderError(f"Gemini API error: {str(e)}") from e
