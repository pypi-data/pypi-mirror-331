# ----- grok.py -----
from typing import Generator

from openai import OpenAI, APIError, APIConnectionError

from llmfusion.base.interfaces import BaseLLM
from llmfusion.base.exceptions import LLMError
from llmfusion.base.models import LLMConfig, LLMInput


class GrokClient(BaseLLM):
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self._client = OpenAI(
            base_url=config.base_url or "https://api.groq.com/v1",
            api_key=config.api_key,
            timeout=config.timeout
        )

    def generate(self, input: LLMInput) -> str:
        try:
            messages = self._build_messages(input)
            response = self._retryable_call(
                self._client.chat.completions.create,
                model=self.config.model_name,
                messages=messages,
                temperature=input.temperature,
                max_tokens=input.max_tokens
            )
            return response.choices[0].message.content
        except APIError as e:
            self._handle_error(e)

    def stream(self, input: LLMInput) -> Generator[str, None, None]:
        messages = self._build_messages(input)
        try:
            stream = self._client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                temperature=input.temperature,
                max_tokens=input.max_tokens,
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            self._handle_error(e)

    def _build_messages(self, input: LLMInput):
        messages = []
        if input.system_prompt:
            messages.append({"role": "system", "content": input.system_prompt})
        messages.append({"role": "user", "content": input.prompt})
        return messages

    def _handle_error(self, error: Exception):
        if isinstance(error, APIConnectionError):
            raise LLMError("Connection error") from error
        raise LLMError(str(error)) from error