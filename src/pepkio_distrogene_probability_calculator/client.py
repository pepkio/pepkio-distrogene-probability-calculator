"""HTTP Client for Pepkio distrogene-probability-calculator tool API."""

import os
import time
from typing import Any, Dict, List, Optional

import httpx

from .config import TOOL_ID, get_default_api_key, get_default_base_url
from .exceptions import PepkioAPIError, PepkioAuthError
from .models import RunResult


def _resolve_verify(base_url: str, verify: Optional[bool]) -> bool:
    if verify is not None:
        return verify
    env_verify = os.environ.get("PEPKIO_VERIFY_SSL")
    if env_verify is not None:
        return env_verify.lower() not in ("false", "0", "no")
    if "localtest.me" in base_url or "localhost" in base_url or "127.0.0.1" in base_url:
        return False
    return True


class PepkioClient:
    """Synchronous Python client for Pepkio distrogene-probability-calculator API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        verify: Optional[bool] = None,
        client: Optional[httpx.Client] = None,
    ):
        """Initialize the Pepkio client.

        Args:
            api_key: API key for authentication. Defaults to PEPKIO_API_KEY environment variable.
            base_url: Base URL for Pepkio API. Defaults to PEPKIO_API_BASE_URL or production.
            timeout: HTTP request timeout in seconds. Defaults to 30.0.
            verify: Whether to verify SSL certificates. Defaults to False for localtest.me.
            client: Optional custom httpx.Client instance.
        """
        self.base_url = (base_url or get_default_base_url()).rstrip("/")
        self.api_key = api_key if api_key is not None else get_default_api_key()
        self.timeout = timeout
        self.verify = _resolve_verify(self.base_url, verify)
        self._client = client
        self._own_client = False

    def _get_client(self) -> httpx.Client:
        if self._client is None or self._client.is_closed:
            self._client = httpx.Client(timeout=self.timeout, verify=self.verify)
            self._own_client = True
        return self._client

    def close(self) -> None:
        """Close the underlying HTTP client if owned."""
        if self._own_client and self._client and not self._client.is_closed:
            self._client.close()

    def __enter__(self) -> "PepkioClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def _headers(self, requires_auth: bool = True) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        elif requires_auth:
            raise PepkioAuthError(
                status_code=401,
                message=(
                    "API key is required for authentication. Set PEPKIO_API_KEY "
                    "environment variable or pass api_key to PepkioClient."
                ),
            )
        return headers

    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        try:
            body = response.json()
        except Exception:
            body = {}

        if response.is_error:
            err_dict = body.get("error", {}) if isinstance(body.get("error"), dict) else {}
            msg = err_dict.get("message") or response.text or f"HTTP {response.status_code}"
            if response.status_code in (401, 403):
                raise PepkioAuthError(response.status_code, msg, body)
            raise PepkioAPIError(response.status_code, msg, body)

        return body

    def get_manifest(self) -> Dict[str, Any]:
        """Fetch the live tool manifest containing input schema and examples.

        Returns:
            Dict containing tool manifest metadata.
        """
        client = self._get_client()
        url = f"{self.base_url}/api/tools/v1/tools/{TOOL_ID}/manifest"
        response = client.get(url, headers=self._headers(requires_auth=False))
        return self._handle_response(response)

    def list_examples(self) -> List[Dict[str, Any]]:
        """List example inputs provided in the tool manifest.

        Returns:
            List of example definitions.
        """
        manifest = self.get_manifest()
        return manifest.get("examples", [])

    def get_example_input(self, example_name: str) -> Dict[str, Any]:
        """Get the input payload for a named example in the manifest.

        Args:
            example_name: Name of example (e.g. 'crispr_coverage', 'go_enrichment').

        Returns:
            Dict representing example tool input.
        """
        examples = self.list_examples()
        for ex in examples:
            if ex.get("name") == example_name:
                return ex.get("input", {})
        valid_names = [ex.get("name") for ex in examples if "name" in ex]
        raise ValueError(
            f"Example '{example_name}' not found in manifest. Available examples: {valid_names}"
        )

    def run(
        self,
        input_data: Dict[str, Any],
        label: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        share: Optional[bool] = None,
    ) -> RunResult:
        """Run the distrogene-probability-calculator tool.

        Args:
            input_data: Input parameters dict matching tool manifest input schema.
            label: Optional label for run identification.
            idempotency_key: Optional key for idempotent run requests.
            share: Optional boolean to enable public sharing.

        Returns:
            RunResult object.
        """
        client = self._get_client()
        url = f"{self.base_url}/api/tools/v1/tools/{TOOL_ID}/run"

        options: Dict[str, Any] = {}
        if label is not None:
            options["label"] = label
        if idempotency_key is not None:
            options["idempotency_key"] = idempotency_key
        if share is not None:
            options["share"] = share

        payload: Dict[str, Any] = {"input": input_data}
        if options:
            payload["options"] = options

        response = client.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json", **self._headers(requires_auth=True)},
        )
        body = self._handle_response(response)
        result = RunResult.model_validate(body)
        result.raise_for_error()
        return result

    def get_run(self, run_id: str) -> RunResult:
        """Retrieve details and status of a previous run by run ID.

        Args:
            run_id: Unique ID of the run.

        Returns:
            RunResult object.
        """
        client = self._get_client()
        url = f"{self.base_url}/api/tools/v1/runs/{run_id}"
        response = client.get(url, headers=self._headers(requires_auth=True))
        body = self._handle_response(response)
        result = RunResult.model_validate(body)
        return result

    def wait_for_run(
        self, run_id: str, poll_interval: float = 1.0, max_attempts: int = 60
    ) -> RunResult:
        """Poll run status until execution is completed or failed.

        Args:
            run_id: Unique ID of the run.
            poll_interval: Interval in seconds between status polls.
            max_attempts: Maximum number of polling attempts.

        Returns:
            RunResult object.
        """
        for _ in range(max_attempts):
            res = self.get_run(run_id)
            if res.status not in ("queued", "running"):
                res.raise_for_error()
                return res
            time.sleep(poll_interval)
        raise TimeoutError(f"Run {run_id} did not complete within {max_attempts * poll_interval}s")


class AsyncPepkioClient:
    """Asynchronous Python client for Pepkio distrogene-probability-calculator API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        verify: Optional[bool] = None,
        client: Optional[httpx.AsyncClient] = None,
    ):
        self.base_url = (base_url or get_default_base_url()).rstrip("/")
        self.api_key = api_key if api_key is not None else get_default_api_key()
        self.timeout = timeout
        self.verify = _resolve_verify(self.base_url, verify)
        self._client = client
        self._own_client = False

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout, verify=self.verify)
            self._own_client = True
        return self._client

    async def close(self) -> None:
        if self._own_client and self._client and not self._client.is_closed:
            await self._client.aclose()

    async def __aenter__(self) -> "AsyncPepkioClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    def _headers(self, requires_auth: bool = True) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        elif requires_auth:
            raise PepkioAuthError(
                status_code=401,
                message=(
                    "API key is required for authentication. Set PEPKIO_API_KEY "
                    "environment variable or pass api_key to AsyncPepkioClient."
                ),
            )
        return headers

    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        try:
            body = response.json()
        except Exception:
            body = {}

        if response.is_error:
            err_dict = body.get("error", {}) if isinstance(body.get("error"), dict) else {}
            msg = err_dict.get("message") or response.text or f"HTTP {response.status_code}"
            if response.status_code in (401, 403):
                raise PepkioAuthError(response.status_code, msg, body)
            raise PepkioAPIError(response.status_code, msg, body)

        return body

    async def get_manifest(self) -> Dict[str, Any]:
        client = self._get_client()
        url = f"{self.base_url}/api/tools/v1/tools/{TOOL_ID}/manifest"
        response = await client.get(url, headers=self._headers(requires_auth=False))
        return self._handle_response(response)

    async def list_examples(self) -> List[Dict[str, Any]]:
        manifest = await self.get_manifest()
        return manifest.get("examples", [])

    async def get_example_input(self, example_name: str) -> Dict[str, Any]:
        examples = await self.list_examples()
        for ex in examples:
            if ex.get("name") == example_name:
                return ex.get("input", {})
        valid_names = [ex.get("name") for ex in examples if "name" in ex]
        raise ValueError(
            f"Example '{example_name}' not found in manifest. Available examples: {valid_names}"
        )

    async def run(
        self,
        input_data: Dict[str, Any],
        label: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        share: Optional[bool] = None,
    ) -> RunResult:
        client = self._get_client()
        url = f"{self.base_url}/api/tools/v1/tools/{TOOL_ID}/run"

        options: Dict[str, Any] = {}
        if label is not None:
            options["label"] = label
        if idempotency_key is not None:
            options["idempotency_key"] = idempotency_key
        if share is not None:
            options["share"] = share

        payload: Dict[str, Any] = {"input": input_data}
        if options:
            payload["options"] = options

        response = await client.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json", **self._headers(requires_auth=True)},
        )
        body = self._handle_response(response)
        result = RunResult.model_validate(body)
        result.raise_for_error()
        return result

    async def get_run(self, run_id: str) -> RunResult:
        client = self._get_client()
        url = f"{self.base_url}/api/tools/v1/runs/{run_id}"
        response = await client.get(url, headers=self._headers(requires_auth=True))
        body = self._handle_response(response)
        result = RunResult.model_validate(body)
        return result
