import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


class ConfigError(Exception):
    """Raised when required configuration is missing."""
    pass


def _get_required_env(var_name: str) -> str:
    """
    Fetch a required environment variable.
    Raise a clear error if it does not exist.
    """
    value = os.getenv(var_name)

    if not value:
        raise ConfigError(
            f"Missing required environment variable: '{var_name}'. "
            f"Please add it to your .env file."
        )

    return value


# ------------------------------------------------------------------
# API Keys
# ------------------------------------------------------------------

GROQ_API_KEY: str = _get_required_env("GROQ_API_KEY")
TAVILY_API_KEY: str = _get_required_env("TAVILY_API_KEY")


# ------------------------------------------------------------------
# Groq Model Settings
# ------------------------------------------------------------------

GROQ_MODEL_NAME: str = "llama-3.1-8b-instant"

GROQ_TEMPERATURE: float = 0.4

GROQ_MAX_TOKENS: int = 1024


# ------------------------------------------------------------------
# Tavily Search Settings
# ------------------------------------------------------------------

TAVILY_MAX_RESULTS: int = 3

TAVILY_SEARCH_DEPTH: str = "basic"


# ------------------------------------------------------------------
# Application Constants
# ------------------------------------------------------------------

APP_TITLE: str = "AI-Powered Research & Recommendation Agent"