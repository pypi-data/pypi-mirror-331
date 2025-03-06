from typing import Dict, List, Optional, Tuple, Any
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
    last_used: float = 0.0
    usage_count: int = 0
    failed_attempts: int = 0
    is_active: bool = True
    cost_per_token: float = 0.0  # USD per token
    rate_limit: Optional[int] = None  # Requests per minute (RPM)
    last_failure_time: Optional[float] = None  # Timestamp of the last failure

    def fingerprint(self) -> str:
        return hashlib.sha256(self.key.encode()).hexdigest()[:8]


class KeyManager:
    def __init__(self,
                 keys: Optional[List[str]] = None,
                 env_file: Optional[str] = None,
                 cost_map_file: Optional[str] = None,
                 failure_threshold: int = 3,
                 cooldown_period: float = 60.0):
        """
        failure_threshold: Number of consecutive failures before disabling a key.
        cooldown_period: Seconds after which a disabled key can be retried automatically.
        """
        if env_file:
            load_dotenv(env_file)
        self.keys: List[Tuple[str, APIKey]] = self._load_keys_from_env(keys)
        self.provider_indices: Dict[str, int] = {}  # Maintain a round-robin index per provider.
        self.lock = Lock()
        # Track usage stats with keys: (fingerprint, minute).
        self.usage_stats = defaultdict(lambda: {'success': 0, 'failure': 0, 'tokens': 0, 'cost': 0.0})
        self.cost_map = self._load_cost_map(cost_map_file)
        self.failure_threshold = failure_threshold
        self.cooldown_period = cooldown_period

    def _load_keys_from_env(self, explicit_keys: Optional[List[str]]) -> List[Tuple[str, APIKey]]:
        keys: List[Tuple[str, APIKey]] = []
        for key, value in os.environ.items():
            if key.endswith("_API_KEYS"):
                provider = key[:-9].lower()  # e.g., "openai" from "OPENAI_API_KEYS"
                for api_key in value.split(','):
                    if api_key.strip():
                        keys.append((provider, APIKey(key=api_key.strip())))
            elif key.endswith("_API_KEY"):
                provider = key[:-8].lower()  # e.g., "openai" from "OPENAI_API_KEY"
                keys.append((provider, APIKey(key=value.strip())))
        if explicit_keys:
            for api_key in explicit_keys:
                if api_key.strip():
                    keys.append(("global", APIKey(key=api_key.strip())))
        return keys

    def _load_cost_map(self, cost_map_file: Optional[str]) -> Dict[str, Dict[str, float]]:
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
        """Retrieve keys for a specific provider (including global keys)."""
        return [key for (prov, key) in self.keys if prov == provider or prov == "global"]

    def get_next_key(self, provider: str, model: str) -> Tuple[APIKey, float]:
        """
        Get the next available key for a specific provider and model using round-robin selection.
        Automatically re-enables keys if the cooldown period has passed.
        Raises a RuntimeError if no active key meets the criteria.
        """
        with self.lock:
            provider_keys = self.get_keys_for_provider(provider)
            if not provider_keys:
                raise RuntimeError(f"No keys available for provider: {provider}")

            current_index = self.provider_indices.get(provider, 0)
            attempts = 0
            num_keys = len(provider_keys)

            while attempts < num_keys:
                key = provider_keys[current_index]
                current_index = (current_index + 1) % num_keys
                attempts += 1

                # Automatic key recovery: if a key is disabled and cooldown has passed, re-enable it.
                if not key.is_active and key.last_failure_time:
                    if time.time() - key.last_failure_time >= self.cooldown_period:
                        logger.info(f"Re-enabling key {key.fingerprint()} after cooldown.")
                        key.is_active = True
                        key.failed_attempts = 0

                if key.is_active and self._check_rate_limit(key):
                    key.last_used = time.time()
                    self.provider_indices[provider] = current_index
                    cost = self._get_cost_per_token(provider, model)
                    return key, cost

            raise RuntimeError(f"No active API keys available for provider: {provider}")

    def _get_cost_per_token(self, provider: str, model: str) -> float:
        try:
            return self.cost_map[provider][model]
        except KeyError:
            logger.warning(f"No cost data for {provider}/{model}, using default 0.0")
            return 0.0

    def _check_rate_limit(self, key: APIKey) -> bool:
        if key.rate_limit is None:
            return True
        current_minute = int(time.time() // 60)
        stats = self.usage_stats[(key.fingerprint(), current_minute)]
        current_count = stats['success'] + stats['failure']
        return current_count < key.rate_limit

    def record_usage(self, key: APIKey, tokens: int, success: bool) -> None:
        """
        Record usage statistics for a key. On failure, increments the failure count and disables the key
        if the failure threshold is reached.
        """
        with self.lock:
            fingerprint = key.fingerprint()
            current_minute = int(time.time() // 60)
            stats = self.usage_stats[(fingerprint, current_minute)]
            stats['tokens'] += tokens
            stats['cost'] += tokens * key.cost_per_token

            if success:
                stats['success'] += 1
                key.usage_count += 1
                key.failed_attempts = 0
            else:
                stats['failure'] += 1
                key.failed_attempts += 1
                key.last_failure_time = time.time()
                if key.failed_attempts >= self.failure_threshold:
                    key.is_active = False
                    logger.error(f"Key {fingerprint} disabled due to {key.failed_attempts} consecutive failures.")

    def cleanup_usage_stats(self, max_age_minutes: int = 60) -> None:
        """
        Remove usage statistics older than max_age_minutes to prevent unbounded growth.
        """
        with self.lock:
            current_minute = int(time.time() // 60)
            keys_to_delete = []
            for (fp, minute) in list(self.usage_stats.keys()):
                if current_minute - minute > max_age_minutes:
                    keys_to_delete.append((fp, minute))
            for key in keys_to_delete:
                del self.usage_stats[key]
            logger.info(f"Cleaned up {len(keys_to_delete)} old usage stats entries.")

    # --- Dynamic Key Management Methods ---

    def add_key(self, provider: str, key_str: str, cost_per_token: float = 0.0, rate_limit: Optional[int] = None) -> None:
        """
        Add a new key for the given provider.
        """
        with self.lock:
            new_key = APIKey(key=key_str.strip(), cost_per_token=cost_per_token, rate_limit=rate_limit)
            self.keys.append((provider.lower(), new_key))
            logger.info(f"Added new key for provider {provider}: {new_key.fingerprint()}.")

    def remove_key(self, fingerprint: str) -> bool:
        """
        Remove a key by its fingerprint.
        Returns True if the key was found and removed, otherwise False.
        """
        with self.lock:
            for idx, (provider, key) in enumerate(self.keys):
                if key.fingerprint() == fingerprint:
                    del self.keys[idx]
                    logger.info(f"Removed key {fingerprint} for provider {provider}.")
                    return True
        logger.warning(f"Key {fingerprint} not found for removal.")
        return False

    def update_key(self, fingerprint: str, **kwargs: Any) -> bool:
        """
        Update key attributes (e.g., cost_per_token, rate_limit).
        Returns True if the key was found and updated.
        """
        with self.lock:
            for provider, key in self.keys:
                if key.fingerprint() == fingerprint:
                    for attr, value in kwargs.items():
                        if hasattr(key, attr):
                            setattr(key, attr, value)
                    logger.info(f"Updated key {fingerprint} with {kwargs}.")
                    return True
        logger.warning(f"Key {fingerprint} not found for update.")
        return False

    def health_check(self) -> Dict[str, Dict[str, Any]]:
        """
        Perform a basic health check on all keys, returning their status.
        """
        report = {}
        with self.lock:
            for provider, key in self.keys:
                report[key.fingerprint()] = {
                    'provider': provider,
                    'is_active': key.is_active,
                    'failed_attempts': key.failed_attempts,
                    'last_used': key.last_used,
                    'rate_limit': key.rate_limit,
                    'cost_per_token': key.cost_per_token
                }
        return report

    def get_usage_report(self) -> dict:
        """
        Generate a comprehensive usage report, including overall statistics and per-key details.
        """
        report = {
            'total_usage': {'tokens': 0, 'cost': 0.0, 'requests': 0},
            'key_details': {},
            'current_active': []
        }
        with self.lock:
            for stats in self.usage_stats.values():
                report['total_usage']['tokens'] += stats['tokens']
                report['total_usage']['cost'] += stats['cost']
                report['total_usage']['requests'] += stats['success'] + stats['failure']

            for (provider, key) in self.keys:
                fp = key.fingerprint()
                report['key_details'][fp] = {
                    'provider': provider,
                    'usage_count': key.usage_count,
                    'failed_attempts': key.failed_attempts,
                    'is_active': key.is_active,
                    'last_used': key.last_used
                }
                if key.is_active:
                    report['current_active'].append(fp)
        return report
