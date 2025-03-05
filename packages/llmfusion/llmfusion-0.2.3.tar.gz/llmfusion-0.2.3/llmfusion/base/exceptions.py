from typing import Optional


class LLMError(Exception):
    """Base exception for all LLM errors"""


class RateLimitError(LLMError):
    """Raised when rate limit is exceeded"""


class AuthenticationError(LLMError):
    """Raised for authentication issues"""


class ProviderError(LLMError):
    """Provider-specific error"""


# In your base/exceptions.py file

class InputValidationError(ValueError):
    """Exception raised for invalid input to LLM providers."""

    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        if self.field:
            return f"Invalid input for field '{self.field}': {self.message}"
        return f"Invalid input: {self.message}"

    def __str__(self) -> str:
        return self._format_message()