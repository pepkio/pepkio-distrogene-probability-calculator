"""Unit tests for pepkio-distrogene-probability-calculator with mocked HTTP responses."""

from unittest.mock import patch

import httpx
import pytest
from click.testing import CliRunner

from pepkio_distrogene_probability_calculator import (
    DEFAULT_API_BASE_URL,
    AsyncPepkioClient,
    PepkioAuthError,
    PepkioClient,
    PepkioRunError,
    RunResult,
)
from pepkio_distrogene_probability_calculator.cli import main


def test_client_init_defaults(monkeypatch):
    monkeypatch.delenv("PEPKIO_API_BASE_URL", raising=False)
    monkeypatch.delenv("PEPKIO_API_KEY", raising=False)

    client = PepkioClient()
    assert client.base_url == DEFAULT_API_BASE_URL
    assert client.api_key is None


def test_client_init_custom():
    client = PepkioClient(api_key="test_key", base_url="https://custom.pepkio.com/")
    assert client.base_url == "https://custom.pepkio.com"
    assert client.api_key == "test_key"


def test_get_manifest_mock():
    mock_manifest = {
        "tool_id": "distrogene-probability-calculator",
        "title": "DistroGene Probability Calculator",
        "examples": [{"name": "crispr_coverage", "input": {"scenario": "crispr_coverage"}}],
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/tools/v1/tools/distrogene-probability-calculator/manifest"
        return httpx.Response(200, json=mock_manifest)

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as httpx_client:
        client = PepkioClient(client=httpx_client)
        manifest = client.get_manifest()
        assert manifest["tool_id"] == "distrogene-probability-calculator"
        assert client.list_examples() == [
            {"name": "crispr_coverage", "input": {"scenario": "crispr_coverage"}}
        ]
        assert client.get_example_input("crispr_coverage") == {"scenario": "crispr_coverage"}


def test_run_mock_success():
    mock_run_response = {
        "run_id": "run-12345",
        "status": "completed",
        "result": {
            "ready": True,
            "probability": 0.993,
            "interpretation": "99.3% probability",
        },
        "error": None,
        "result_url": "https://tools.pepkio.com/api/tools/v1/runs/run-12345",
        "permalink": "https://tools.pepkio.com/r/run-12345",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/tools/v1/tools/distrogene-probability-calculator/run"
        assert request.headers.get("Authorization") == "Bearer secret_key"
        return httpx.Response(200, json=mock_run_response)

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as httpx_client:
        client = PepkioClient(api_key="secret_key", client=httpx_client)
        res = client.run({"scenario": "crispr_coverage", "mode": "forward", "tail": "ge"})
        assert isinstance(res, RunResult)
        assert res.run_id == "run-12345"
        assert res.status == "completed"
        assert res.result["probability"] == 0.993


def test_auth_error_missing_key():
    client = PepkioClient(api_key=None)
    with pytest.raises(PepkioAuthError) as exc_info:
        client.run({"scenario": "crispr_coverage"})
    assert "API key is required" in str(exc_info.value)


def test_auth_error_invalid_key():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": {"message": "Invalid API key"}})

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as httpx_client:
        client = PepkioClient(api_key="bad_key", client=httpx_client)
        with pytest.raises(PepkioAuthError) as exc_info:
            client.run({"scenario": "crispr_coverage"})
        assert exc_info.value.status_code == 401
        assert "Invalid API key" in str(exc_info.value)


def test_run_error_handling():
    mock_run_error = {
        "run_id": "run-fail-1",
        "status": "failed",
        "result": None,
        "error": "Invalid parameters",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=mock_run_error)

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as httpx_client:
        client = PepkioClient(api_key="secret_key", client=httpx_client)
        with pytest.raises(PepkioRunError) as exc_info:
            client.run({"scenario": "invalid"})
        assert exc_info.value.run_id == "run-fail-1"


@pytest.mark.asyncio
async def test_async_client_mock():
    mock_manifest = {"tool_id": "distrogene-probability-calculator"}

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=mock_manifest)

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as async_httpx_client:
        async with AsyncPepkioClient(client=async_httpx_client) as client:
            manifest = await client.get_manifest()
            assert manifest["tool_id"] == "distrogene-probability-calculator"


def test_cli_manifest():
    runner = CliRunner()
    mock_manifest = {"tool_id": "distrogene-probability-calculator", "title": "Test Title"}

    with patch.object(PepkioClient, "get_manifest", return_value=mock_manifest):
        result = runner.invoke(main, ["manifest"])
        assert result.exit_code == 0
        assert "distrogene-probability-calculator" in result.output


def test_cli_run_example():
    runner = CliRunner()
    mock_run_result = RunResult(
        run_id="run-cli-1",
        status="completed",
        result={"probability": 0.95},
    )

    with patch.object(
        PepkioClient, "get_example_input", return_value={"scenario": "crispr_coverage"}
    ):
        with patch.object(PepkioClient, "run", return_value=mock_run_result):
            result = runner.invoke(
                main, ["run", "--example", "crispr_coverage", "--api-key", "test_key"]
            )
            assert result.exit_code == 0
            assert "run-cli-1" in result.output
