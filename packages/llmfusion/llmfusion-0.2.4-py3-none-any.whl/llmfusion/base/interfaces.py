import hashlib
import logging
from abc import ABC, abstractmethod
from typing import Generator

import httpx
from diskcache import Cache
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log
)

from llmfusion.base.exceptions import RateLimitError
from llmfusion.base.models import LLMConfig, LLMInput
from llmfusion.utils.rate_limiter import TokenBucketLimiter

logger = logging.getLogger(__name__)
cache = Cache("llm_cache", size_limit=int(1e9))  # 1GB cache


class BaseLLM(ABC):
    def __init__(self, config: LLMConfig):
        self.config = config
        self._client = None
        self._async_client = None
        self._rate_limiter = TokenBucketLimiter(config.rate_limit_rpm // 60)

    @abstractmethod
    def generate(self, input: LLMInput) -> str:
        """Synchronous text generation"""
        pass

    @abstractmethod
    async def agenerate(self, input: LLMInput) -> str:
        """Asynchronous text generation"""
        pass

    @abstractmethod
    def stream(self, input: LLMInput) -> Generator[str, None, None]:
        """Streaming text generation"""
        pass

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=(
                retry_if_exception_type((RateLimitError, httpx.NetworkError)) |
                retry_if_exception_type(httpx.HTTPStatusError)
        ),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def _retryable_call(self, func, *args, **kwargs):
        """Wrapper for retryable operations"""
        with self._rate_limiter:
            return func(*args, **kwargs)

    def _cache_key(self, input: LLMInput) -> str:
        """Generate consistent cache key"""
        key_data = f"{self.__class__.__name__}-{input.json()}"
        return hashlib.sha256(key_data.encode()).hexdigest()
