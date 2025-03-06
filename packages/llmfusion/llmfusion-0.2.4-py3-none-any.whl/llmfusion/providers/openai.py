import openai
import time
from typing import Optional, Dict, Any
from pydantic import BaseModel

from llmfusion.base.models import LLMConfig, LLMInput
from llmfusion.providers.configs.model_global_configs import GlobalModelConfig
from llmfusion.utils.diskcache_ import diskcache_memoize


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

    def _generate(self, prompt: LLMInput, **kwargs) -> str:
        """Core logic to generate completion without caching."""

        messages = self._build_messages(input=prompt)
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

    @diskcache_memoize(expire_tag="get_completion", size_gib="large")
    def _generate_cached(self, prompt: str, **kwargs) -> str:
        """Cached version of _generate."""
        return self._generate(prompt, **kwargs)

    def generate(self, prompt: str, read_cache: bool = True, **kwargs) -> str:
        """
        Generate a text completion.

        Args:
            prompt: User input text.
            read_cache: When False, bypasses cache and makes a fresh API call.
            **kwargs: Additional parameters to override defaults.

        Returns:
            Generated text content.
        """
        if read_cache:
            return self._generate_cached(prompt, **kwargs)
        else:
            return self._generate(prompt, **kwargs)

    def _build_messages(self, input: LLMInput) -> list[dict]:
        messages = []
        if input.system_prompt:
            messages.append({
                "role": "system",
                "content": str(input.system_prompt)
            })
        messages.append({
            "role": "user",
            "content": str(input.prompt)
        })
        return messages

    def _merge_params(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        base_params = {
            "model": self.config.model_name,
            "temperature": self.config.temperature,
            "max_tokens": self.model_spec["max_output_tokens"]
        }
        return {**base_params, **kwargs}

    def _handle_retry(self, error: Exception, attempt: int) -> None:
        sleep_time = 2 ** attempt
        print(f"Retry {attempt + 1}/{self.config.max_retries} in {sleep_time}s")
        time.sleep(sleep_time)




class RateLimitError(Exception):
    """Custom exception for rate limiting"""


class APIError(Exception):
    """Custom exception for general API errors"""