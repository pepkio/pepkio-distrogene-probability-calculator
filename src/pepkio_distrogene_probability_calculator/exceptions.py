# SPDX-License-Identifier: MIT
"""Exception definitions for pepkio-distrogene-probability-calculator."""

from typing import Any, Dict, Optional


class PepkioError(Exception):
    """Base exception for Pepkio client errors."""

    pass


class PepkioAPIError(PepkioError):
    """Raised when the Pepkio REST API returns an HTTP error (4xx/5xx)."""

    def __init__(self, status_code: int, message: str, body: Optional[Dict[str, Any]] = None):
        super().__init__(f"API error ({status_code}): {message}")
        self.status_code = status_code
        self.message = message
        self.body = body or {}


class PepkioAuthError(PepkioAPIError):
    """Raised when authentication fails (401/403)."""

    def __init__(self, status_code: int, message: str, body: Optional[Dict[str, Any]] = None):
        super().__init__(status_code, message, body)


class PepkioRunError(PepkioError):
    """Raised when a tool run fails or returns an error payload."""

    def __init__(self, run_id: str, error: Any):
        super().__init__(f"Run {run_id} failed: {error}")
        self.run_id = run_id
        self.error = error
