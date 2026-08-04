# Pepkio DistroGene Probability Calculator

Python client for the Pepkio DistroGene Probability Calculator API: calculate CRISPR coverage, GO enrichment, variant detection, and barcode collision probabilities with reverse sizing and publication Methods text export.

## Overview

The DistroGene Probability Calculator provides statistical calculations for genomics experiments, including Poisson CRISPR library coverage, hypergeometric GO enrichment, binomial variant detection, barcode collision analysis, and negative binomial overdispersed library modeling.

This Python client (`pepkio-distrogene-probability-calculator`) allows researchers to run probability calculations programmatically from scripts, Jupyter notebooks, or CI pipelines without using the web UI.

Hosted web app: [https://www.pepkio.com/tools/distrogene-probability-calculator](https://www.pepkio.com/tools/distrogene-probability-calculator)

## Installation

```bash
pip install pepkio-distrogene-probability-calculator
```

Set your API key as an environment variable:

```bash
export PEPKIO_API_KEY="your-api-key"
```

## Quick Start

### Python API

```python
from pepkio_distrogene_probability_calculator import PepkioClient

client = PepkioClient()

# Fetch manifest and available examples
manifest = client.get_manifest()
print(manifest["title"])

# Run CRISPR coverage calculation
result = client.run(
    {
        "scenario": "crispr_coverage",
        "mode": "forward",
        "tail": "ge",
        "library_size": 80000,
        "total_reads": 400000,
        "threshold_k": 1,
    }
)

print(f"Probability: {result.result['probability']}")
print(f"Interpretation: {result.result['interpretation']}")
print(f"Methods text: {result.result['methods_text']}")
```

### CLI

```bash
# View tool manifest
pepkio-distrogene-probability-calculator manifest

# Run built-in example
pepkio-distrogene-probability-calculator run --example crispr_coverage

# Run custom input JSON
pepkio-distrogene-probability-calculator run --input-json '{"scenario":"variant_detection","mode":"forward","tail":"ge","sequencing_reads":10000,"allele_frequency":0.05,"variant_reads":3}'
```

## Environment Variables

- `PEPKIO_API_KEY`: API key for Pepkio tools API (required for running tools).
- `PEPKIO_API_BASE_URL`: Base URL override (default: `https://tools.pepkio.com`).

## Publishing

To publish a new version to PyPI:

```bash
source ~/.bash_profile # loads POETRY_PYPI_TOKEN_PYPI
uv build
uv publish --token "$POETRY_PYPI_TOKEN_PYPI"
```
