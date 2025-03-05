import openai
import time
from typing import Optional, Dict, Any
from pydantic import BaseModel

from llmfusion.base.models import LLMConfig, LLMInput
from llmfusion.providers.configs.model_global_configs import GlobalModelConfig
from llmfusion.utils.diskcache_ import diskcache_memoize


# Import your custom decorator




class OpenAIClient:
    def __init__(self, config: LLMConfig):
        self.config = config
        llm_key, cost = config.key_manager.get_next_key(provider="openai", model=config.model_name)
        api_key_str = llm_key.key
        self.model_spec = GlobalModelConfig().get_model_spec("openai", config.model_name)
        self.client = openai.OpenAI(
            api_key=api_key_str,
            timeout=config.timeout
        )

    @diskcache_memoize(expire_tag="get_completion", size_gib="large")
    def generate(
            self,
            prompt: str,
            **kwargs
    ) -> str:
        """Generate text completion with caching and retries.

        Args:
            prompt: User input text
            system_prompt: Optional system message
            **kwargs: Overrides for default parameters

        Returns:
            Generated text content

        Raises:
            RateLimitError: When rate limits are exceeded
            APIError: For other API-related errors
        """
        messages = self._build_messages(prompt)
        params = self._merge_params(kwargs)

        for attempt in range(self.config.max_retries):
            try:
                response = self.client.chat.completions.create(
                    messages=messages,
                    **params
                )
                return response.choices[0].message.content

            except openai.RateLimitError as e:
                if attempt == self.config.max_retries - 1:
                    raise RuntimeError(f"Rate limit exceeded: {str(e)}") from e
                self._handle_retry(e, attempt)

            except openai.APIError as e:
                raise RuntimeError(f"API error: {str(e)}") from e

    def _build_messages(self, input: LLMInput) -> list[dict]:
        """Properly format messages for OpenAI API"""
        messages = []

        if input.system_prompt:
            messages.append({
                "role": "system",
                "content": str(input.system_prompt)  # Ensure string conversion
            })

        messages.append({
            "role": "user",
            "content": str(input.prompt)  # Ensure string conversion
        })

        return messages

    def _merge_params(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Merge default config with override parameters"""
        base_params = {
            "model": self.config.model_name,
            "temperature": self.config.temperature,
            "max_tokens": self.model_spec["max_output_tokens"]
        }
        return {**base_params, **kwargs}

    def _handle_retry(self, error: Exception, attempt: int) -> None:
        """Handle retry logic with exponential backoff"""
        sleep_time = 2 ** attempt
        print(f"Retry {attempt + 1}/{self.config.max_retries} in {sleep_time}s")
        time.sleep(sleep_time)


class RateLimitError(Exception):
    """Custom exception for rate limiting"""


class APIError(Exception):
    """Custom exception for general API errors"""