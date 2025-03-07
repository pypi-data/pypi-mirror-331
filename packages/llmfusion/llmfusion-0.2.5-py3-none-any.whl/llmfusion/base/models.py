import logging
from pathlib import Path
from typing import Optional, Any

from diskcache import Cache
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)
cache = Cache("llm_cache", size_limit=int(1e9))  # 1GB cache




class LLMConfig(BaseModel):
    api_key: Optional[str] = Field(None, env="LLM_API_KEY")
    model_name: str
    base_url: Optional[str] = None
    timeout: int = 30
    temperature: float = 0.7
    max_retries: int = 3
    cache_ttl: int = 3600  # 1 hour
    rate_limit_rpm: int = 1000
    key_manager: Optional[Any] = None
    cache_dir: Optional[str] = None  # Set the cache directory

    def resolved_cache_dir(self) -> Path:
        return Path(self.cache_dir) if self.cache_dir else Path.home() / ".cache" / "llmfusion"

class LLMInput(BaseModel):
    prompt: str
    system_prompt: Optional[str] = None
    temperature: float = Field(0.7, ge=0, le=2)
    max_tokens: int = Field(512, gt=0)

    @validator('prompt')
    def prompt_not_empty(cls, v):
        if len(v.strip()) == 0:
            raise ValueError("Prompt cannot be empty")
        return v
