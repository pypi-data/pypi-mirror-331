from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel
import time
import hashlib
from collections import defaultdict
from threading import Lock
import logging
import os
from dotenv import load_dotenv
import json

logger = logging.getLogger(__name__)


class APIKey(BaseModel):
    key: str
    last_used: float = 0
    usage_count: int = 0
    failed_attempts: int = 0
    is_active: bool = True
    cost_per_token: float = 0  # USD per token
    rate_limit: Optional[int] = None  # RPM

    def fingerprint(self) -> str:
        return hashlib.sha256(self.key.encode()).hexdigest()[:8]


class KeyManager:
    def __init__(self, keys: Optional[List[str]] = None, env_file: Optional[str] = None,
                 cost_map_file: Optional[str] = None):
        # Load environment variables from .env file if provided
        if env_file:
            load_dotenv(env_file)

        # Load all API keys from environment variables
        self.keys = self._load_keys_from_env(keys)

        self.current_index = 0
        self.lock = Lock()
        self.usage_stats = defaultdict(lambda: {
            'success': 0,
            'failure': 0,
            'tokens': 0,
            'cost': 0.0
        })

        # Load cost_map from external JSON file
        self.cost_map = self._load_cost_map(cost_map_file)

    def _load_keys_from_env(self, explicit_keys: Optional[List[str]]) -> List[Tuple[str, APIKey]]:
        """Load API keys from environment variables and merge with explicit keys."""
        keys = []

        # Load keys from environment variables
        for key, value in os.environ.items():
            if key.endswith("_API_KEYS"):
                provider = key[:-9].lower()  # Extract provider name (e.g., "openai" from "OPENAI_API_KEYS")
                for api_key in value.split(','):
                    if api_key.strip():
                        keys.append((provider, APIKey(key=api_key.strip())))
            elif key.endswith("_API_KEY"):
                provider = key[:-8].lower()  # Extract provider name (e.g., "openai" from "OPENAI_API_KEY")
                keys.append((provider, APIKey(key=value)))

        # Add explicit keys (if provided) and override duplicates
        if explicit_keys:
            for api_key in explicit_keys:
                if api_key.strip():
                    # Explicit keys are assumed to be for all providers
                    keys.append(("global", APIKey(key=api_key.strip())))

        return keys

    def _load_cost_map(self, cost_map_file: Optional[str]) -> Dict[str, Dict[str, float]]:
        """Load cost_map from an external JSON file."""
        if not cost_map_file or not os.path.exists(cost_map_file):
            logger.warning(f"Cost map file '{cost_map_file}' not found. Using default empty cost map.")
            return {}

        try:
            with open(cost_map_file, 'r') as file:
                return json.load(file)
        except Exception as e:
            logger.error(f"Failed to load cost map from '{cost_map_file}': {e}")
            return {}

    def get_keys_for_provider(self, provider: str) -> List[APIKey]:
        """Retrieve keys for a specific provider."""
        return [key for (prov, key) in self.keys if prov == provider or prov == "global"]

    def get_next_key(self, provider: str, model: str) -> Tuple[APIKey, float]:
        """Get the next available key for a specific provider and model."""
        with self.lock:
            provider_keys = self.get_keys_for_provider(provider)
            if not provider_keys:
                raise RuntimeError(f"No keys available for provider: {provider}")

            original_index = self.current_index
            attempts = 0

            while attempts < len(provider_keys):
                key = provider_keys[self.current_index]
                self.current_index = (self.current_index + 1) % len(provider_keys)

                if key.is_active:
                    if self._check_rate_limit(key, model):
                        key.last_used = time.time()
                        return key, self._get_cost_per_token(provider, model)

                attempts += 1
                if self.current_index == original_index:
                    break

            raise RuntimeError(f"No active API keys available for provider: {provider}")

    def _get_cost_per_token(self, provider: str, model: str) -> float:
        """Get the cost per token for a specific provider and model."""
        try:
            return self.cost_map[provider][model]
        except KeyError:
            logger.warning(f"No cost data for {provider}/{model}, using default 0.0")
            return 0.0

    def _check_rate_limit(self, key: APIKey, model: str) -> bool:
        """Check if the key is within its rate limit."""
        if key.rate_limit is None:
            return True

        current_minute = time.time() // 60
        minute_stats = self.usage_stats[(key.fingerprint(), current_minute)]
        return minute_stats['count'] < key.rate_limit

    def record_usage(self, key: APIKey, tokens: int, success: bool):
        """Record usage statistics for a key."""
        with self.lock:
            fingerprint = key.fingerprint()
            current_minute = time.time() // 60

            self.usage_stats[(fingerprint, current_minute)]['tokens'] += tokens
            self.usage_stats[(fingerprint, current_minute)]['cost'] += tokens * key.cost_per_token

            if success:
                self.usage_stats[(fingerprint, current_minute)]['success'] += 1
                key.usage_count += 1
                key.failed_attempts = 0
            else:
                self.usage_stats[(fingerprint, current_minute)]['failure'] += 1
                key.failed_attempts += 1

                if key.failed_attempts >= 3:
                    key.is_active = False
                    logger.error(f"Key {fingerprint} disabled due to multiple failures")

    def get_usage_report(self) -> dict:
        """Generate a usage report."""
        report = {
            'total_usage': defaultdict(int),
            'key_details': {},
            'current_active': []
        }

        for (fp, minute), stats in self.usage_stats.items():
            report['total_usage']['tokens'] += stats['tokens']
            report['total_usage']['cost'] += stats['cost']
            report['total_usage']['requests'] += stats['success'] + stats['failure']

        for (provider, key) in self.keys:
            report['key_details'][key.fingerprint()] = {
                'provider': provider,
                'usage_count': key.usage_count,
                'failed_attempts': key.failed_attempts,
                'is_active': key.is_active,
                'last_used': key.last_used
            }
            if key.is_active:
                report['current_active'].append(key.fingerprint())

        return report