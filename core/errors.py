"""User-facing exception types for Phase 1 error handling."""


class AssistantError(Exception):
    """Base class for user-facing assistant errors."""

    default_message = "An assistant error occurred."

    @property
    def user_message(self) -> str:
        return str(self) or self.default_message


class ConfigurationError(AssistantError):
    """Raised when local configuration or prompt files are invalid."""

    default_message = "Configuration is invalid."


class MissingConfigError(ConfigurationError):
    """Raised when the configured settings file cannot be found."""

    default_message = "Configuration file is missing."


class MissingSecretError(ConfigurationError):
    """Raised when a required secret environment variable is missing."""

    default_message = "A required secret is missing."


class InputValidationError(AssistantError):
    """Raised when CLI input fails Phase 1 validation rules."""

    default_message = "Input is invalid."


class ProviderError(AssistantError):
    """Base class for provider request failures."""

    default_message = "The provider request failed."

    def __init__(self, *args: object, log_error: str | None = None) -> None:
        super().__init__(*args)
        self.log_error = log_error


class ProviderAuthenticationError(ProviderError):
    """Raised when the provider rejects authentication credentials."""

    default_message = "Provider authentication failed."


class ProviderRateLimitError(ProviderError):
    """Raised when the provider reports a rate-limit condition."""

    default_message = "Provider rate limit reached."


class ProviderTimeoutError(ProviderError):
    """Raised when the provider request exceeds the configured timeout."""

    default_message = "Provider request timed out."


class ProviderUnavailableError(ProviderError):
    """Raised when the provider is unavailable or returns unusable output."""

    default_message = "Provider is unavailable."


class LogWriteError(AssistantError):
    """Raised when a local interaction log record cannot be written."""

    default_message = "Interaction logging failed."
