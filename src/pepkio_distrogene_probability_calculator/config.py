"""Configuration and environment resolution for distrogene-probability-calculator."""

import os

DEFAULT_API_BASE_URL = "https://tools.pepkio.com"
TOOL_ID = "distrogene-probability-calculator"


def get_default_base_url() -> str:
    """Get default API base URL from PEPKIO_API_BASE_URL env var or fallback."""
    return os.environ.get("PEPKIO_API_BASE_URL", DEFAULT_API_BASE_URL).rstrip("/")


def get_default_api_key() -> str | None:
    """Get default API key from PEPKIO_API_KEY environment variable."""
    return os.environ.get("PEPKIO_API_KEY")
