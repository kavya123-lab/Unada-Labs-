import os
import streamlit as st
from dotenv import load_dotenv

# Load local .env file (for local development)
load_dotenv()


class ConfigError(Exception):
    """Raised when required configuration is missing."""
    pass


def _get_required_env(var_name: str) -> str:
    """
    Fetch a required environment variable.

    Priority:
    1. Streamlit Secrets (Cloud)
    2. Local .env file
    """

    # Streamlit Cloud Secrets
    if var_name in st.secrets:
        return st.secrets[var_name]

    # Local .env
    value = os.getenv(var_name)

    if not value:
        raise ConfigError(
            f"Missing required environment variable: '{var_name}'. "
            f"Please add it to Streamlit Secrets or your .env file."
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