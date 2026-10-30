# SPDX-License-Identifier: MIT
"""Command line interface for pepkio-distrogene-probability-calculator."""

import json
import sys
from typing import Optional

import click

from .client import PepkioClient
from .config import DEFAULT_API_BASE_URL
from .exceptions import PepkioError


@click.group()
@click.version_option()
def main():
    """CLI for Pepkio distrogene-probability-calculator tool."""
    pass


@main.command(name="manifest")
@click.option(
    "--base-url",
    "-b",
    default=None,
    help=f"API base URL (default: {DEFAULT_API_BASE_URL})",
)
def manifest_cmd(base_url: Optional[str]):
    """Fetch and print the tool manifest."""
    try:
        with PepkioClient(base_url=base_url) as client:
            manifest = client.get_manifest()
            click.echo(json.dumps(manifest, indent=2))
    except PepkioError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command(name="list-examples")
@click.option(
    "--base-url",
    "-b",
    default=None,
    help=f"API base URL (default: {DEFAULT_API_BASE_URL})",
)
def list_examples_cmd(base_url: Optional[str]):
    """List available input examples from tool manifest."""
    try:
        with PepkioClient(base_url=base_url) as client:
            examples = client.list_examples()
            click.echo(json.dumps(examples, indent=2))
    except PepkioError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command(name="run")
@click.option("--example", "-e", help="Name of example input from manifest to run")
@click.option("--input-json", "-j", help="Input parameters as JSON string")
@click.option(
    "--input-file",
    "-f",
    type=click.Path(exists=True),
    help="Path to JSON file containing input",
)
@click.option("--api-key", "-k", envvar="PEPKIO_API_KEY", help="Pepkio API Key")
@click.option(
    "--base-url",
    "-b",
    envvar="PEPKIO_API_BASE_URL",
    default=None,
    help=f"API base URL (default: {DEFAULT_API_BASE_URL})",
)
@click.option("--label", "-l", help="Optional label for the run")
@click.option("--idempotency-key", help="Optional idempotency key")
def run_cmd(
    example: Optional[str],
    input_json: Optional[str],
    input_file: Optional[str],
    api_key: Optional[str],
    base_url: Optional[str],
    label: Optional[str],
    idempotency_key: Optional[str],
):
    """Run the distrogene-probability-calculator tool."""
    if sum(bool(x) for x in [example, input_json, input_file]) != 1:
        click.echo(
            "Error: Exactly one of --example, --input-json, or --input-file must be provided.",
            err=True,
        )
        sys.exit(1)

    try:
        with PepkioClient(api_key=api_key, base_url=base_url) as client:
            if example:
                input_data = client.get_example_input(example)
            elif input_json:
                input_data = json.loads(input_json)
            elif input_file:
                with open(input_file, "r", encoding="utf-8") as f:
                    input_data = json.load(f)

            result = client.run(
                input_data=input_data,
                label=label,
                idempotency_key=idempotency_key,
            )
            click.echo(json.dumps(result.model_dump(), indent=2))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command(name="get-run")
@click.argument("run_id")
@click.option("--api-key", "-k", envvar="PEPKIO_API_KEY", help="Pepkio API Key")
@click.option(
    "--base-url",
    "-b",
    envvar="PEPKIO_API_BASE_URL",
    default=None,
    help=f"API base URL (default: {DEFAULT_API_BASE_URL})",
)
def get_run_cmd(run_id: str, api_key: Optional[str], base_url: Optional[str]):
    """Fetch run status and results by run ID."""
    try:
        with PepkioClient(api_key=api_key, base_url=base_url) as client:
            result = client.get_run(run_id)
            click.echo(json.dumps(result.model_dump(), indent=2))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
