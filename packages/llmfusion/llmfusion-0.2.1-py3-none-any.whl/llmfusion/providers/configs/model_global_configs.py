import json
from pathlib import Path
from typing import Dict, Any, TypedDict
from pydantic import BaseModel, ValidationError

class ModelSpec(TypedDict):
    max_input_tokens: int
    max_output_tokens: int
    context_window: int

class GlobalModelConfig:
    _instance = None
    _registry: Dict[str, Dict[str, ModelSpec]] = {}


    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._config_path = (
                Path(__file__).parent.parent / "configs" / "models.json"
            ).resolve()
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        try:
            with open(self._config_path) as f:
                raw_config = json.load(f)
            self._validate_config(raw_config)
            for provider in raw_config:
                for model_name in raw_config[provider]:
                    self.register_model(provider, model_name, raw_config[provider][model_name])

        except FileNotFoundError:
            raise RuntimeError(f"Model config file not found: {self._config_path}")
        except json.JSONDecodeError:
            raise RuntimeError(f"Invalid JSON in config file: {self._config_path}")

    def _validate_config(self, config: Dict[str, Any]):
        required_keys = {"max_input_tokens", "max_output_tokens", "context_window"}
        for provider, models in config.items():
            for model_name, specs in models.items():
                missing = required_keys - specs.keys()
                if missing:
                    raise ValidationError(
                        f"Model {provider}/{model_name} missing keys: {missing}"
                    )

    @classmethod
    def register_model(cls, provider: str, model_name: str, spec: ModelSpec):
        """Register a new model specification"""
        if provider not in cls._registry:
            cls._registry[provider] = {}
        cls._registry[provider][model_name] = spec

    @classmethod
    def get_model_spec(cls, provider: str, model_name: str) -> ModelSpec:
        """Get model specifications"""
        try:
            return cls._registry[provider][model_name]
        except KeyError:
            available = "\n".join(cls._registry[provider].keys())
            raise ValueError(
                f"Unknown model '{model_name}' for provider '{provider}'. "
                f"Available models:\n{available}"
            )

    @classmethod
    def get_default_params(cls, provider: str, model_name: str) -> Dict[str, Any]:
        """Get default parameters for a model"""
        spec = cls.get_model_spec(provider, model_name)
        return {
            "max_tokens": spec["max_output_tokens"],
            "max_input_tokens": spec["max_input_tokens"],
            "context_window": spec["context_window"]
        }