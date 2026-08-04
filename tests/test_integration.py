"""Integration tests running against live Pepkio API endpoints (Local & Production)."""

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from pepkio_distrogene_probability_calculator import (
    AsyncPepkioClient,
    PepkioClient,
    RunResult,
)

# Load environment variables from parent workspace .env if available
env_path = Path(__file__).resolve().parents[2] / ".env"
if env_path.exists():
    load_dotenv(env_path)


def get_api_key_and_base_url():
    """Resolve API key and base URL from environment."""
    base_url = os.environ.get("PEPKIO_API_BASE_URL", "https://tools.pepkio.com")
    api_key = os.environ.get("PEPKIO_API_KEY")

    if "localtest.me" in base_url and not api_key:
        api_key = os.environ.get("LOCAL_PEPKIO_API_KEY")

    return base_url, api_key


@pytest.fixture
def api_credentials():
    base_url, api_key = get_api_key_and_base_url()
    if not api_key:
        pytest.skip("PEPKIO_API_KEY / LOCAL_PEPKIO_API_KEY environment variable not set")
    return base_url, api_key


def test_live_manifest(api_credentials):
    base_url, _ = api_credentials
    client = PepkioClient(base_url=base_url)
    manifest = client.get_manifest()
    assert manifest.get("tool_id") == "distrogene-probability-calculator"
    assert "examples" in manifest
    assert len(manifest["examples"]) >= 1


@pytest.mark.parametrize("example_name", ["crispr_coverage", "go_enrichment", "variant_detection"])
def test_live_run_examples(api_credentials, example_name):
    base_url, api_key = api_credentials
    with PepkioClient(api_key=api_key, base_url=base_url) as client:
        input_data = client.get_example_input(example_name)
        result = client.run(input_data, label=f"integration_test_{example_name}")

        assert isinstance(result, RunResult)
        assert result.run_id is not None
        assert result.status == "completed"
        assert result.result is not None
        assert result.result.get("ready") is True
        assert "probability" in result.result
        assert "interpretation" in result.result

        # Verify get_run returns matching run
        fetched_run = client.get_run(result.run_id)
        assert fetched_run.run_id == result.run_id
        assert fetched_run.status == "completed"


@pytest.mark.asyncio
async def test_live_async_client(api_credentials):
    base_url, api_key = api_credentials
    async with AsyncPepkioClient(api_key=api_key, base_url=base_url) as client:
        manifest = await client.get_manifest()
        assert manifest.get("tool_id") == "distrogene-probability-calculator"

        input_data = await client.get_example_input("crispr_coverage")
        result = await client.run(input_data)

        assert result.status == "completed"
        assert result.result.get("ready") is True

        fetched_run = await client.get_run(result.run_id)
        assert fetched_run.run_id == result.run_id
