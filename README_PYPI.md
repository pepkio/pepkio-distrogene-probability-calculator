# Pepkio DistroGene Probability Calculator

A Python interface for computing discrete statistical distributions in genomics and molecular biology, enabling rapid calculation of CRISPR guide coverage, hypergeometric pathway enrichment, rare variant detection limits, and barcode collision frequencies.

# What It Does

The `pepkio-distrogene-probability-calculator` package provides a programmatic Python client for evaluating probability distributions in high-throughput genomics and laboratory assays. It enables researchers to calculate point and cumulative tail probabilities, perform reverse parameter sizing (such as computing required sequencing depth or sample numbers for target confidence levels), and integrate distribution modeling directly into computational pipelines.

# Features

* **Genomic Distribution Scenarios**: Supports Poisson CRISPR sgRNA coverage, Hypergeometric GO/pathway overrepresentation analysis, Binomial low-frequency variant detection, occupancy-based UMI/cell barcode collisions, overdispersed sequencing library modeling, and serial concentration dilutions.
* **Forward and Reverse Solver Modes**: Evaluates cumulative probabilities from experimental inputs or solves for target sample sizes, required read counts, or starting concentrations given a desired confidence threshold.
* **Point and Cumulative Tail Probabilities**: Computes exact point probabilities ($P(X = k)$) as well as upper and lower cumulative tails ($P(X \ge k)$, $P(X \le k)$, $P(X > k)$, $P(X < k)$).
* **Model Organism Presets**: Contains pre-configured gene background sizes for *Homo sapiens*, *Mus musculus*, *Drosophila melanogaster*, *Caenorhabditis elegans*, *Saccharomyces cerevisiae*, and *Arabidopsis thaliana*.
* **Python API & CLI Interfaces**: Provides `PepkioClient` (and asynchronous HTTP handling via `httpx`) alongside a command-line interface (`pepkio-distrogene-probability-calculator`) for shell scripting.

# Installation

Install the package via pip:

```bash
pip install pepkio-distrogene-probability-calculator
```

Set your API key as an environment variable:

```bash
export PEPKIO_API_KEY="your-api-key"
```

# Quick Example

Evaluate the probability of achieving $\ge 1\times$ coverage per guide in an 80,000 sgRNA CRISPR library sequenced at 400,000 total reads:

```python
from pepkio_distrogene_probability_calculator import PepkioClient

client = PepkioClient()

# Calculate Poisson CRISPR library coverage
result = client.run({
    "scenario": "crispr_coverage",
    "mode": "forward",
    "tail": "ge",
    "library_size": 80000,
    "total_reads": 400000,
    "threshold_k": 1,
})

print(f"Probability: {result.result['probability']}")
print(f"Interpretation: {result.result['interpretation']}")
```

Run built-in examples from the command-line interface:

```bash
pepkio-distrogene-probability-calculator run --example crispr_coverage
```

# Typical Use Cases

* **CRISPR Screen Depth Planning**: Determine minimum sequencing read depth required for adequate sgRNA sampling ($\ge 100\times$ or $\ge 500\times$) in pooled knockout or activation screens.
* **Gene Ontology (GO) Enrichment**: Execute exact Hypergeometric overrepresentation tests comparing query gene sets against whole-genome backgrounds.
* **Variant Detection Limits**: Calculate the statistical confidence of detecting low-frequency mutations ($< 1\%$ VAF) at specific NGS sequencing depths.
* **UMI & Cell Barcode Collision Assessment**: Estimate droplet scRNA-seq barcode duplicate collision rates using occupancy models.
* **Assay Dilution & Standard Curve Setup**: Compute multi-step serial dilution series volumes and concentrations ($C_1 V_1 = C_2 V_2$) for qPCR and ELISA standard curves.

# Scientific Background

Genomic experiments depend on discrete probability distributions to model discrete biological sampling events:
* **Poisson Distribution**: Models random sampling of sgRNAs or sequencing reads across large library spaces under independent draw assumptions.
* **Hypergeometric Distribution**: Computes exact sampling without replacement to test if an observed gene overlap in a pathway exceeds random expectation.
* **Binomial & Negative Binomial Distributions**: Model independent trial successes (variant read counts) and accommodate overdispersed sequencing counts across biological replicates.
* **Occupancy Models**: Solve classical urn and birthday allocation problems to predict UMI or single-cell droplet barcode overlap rates.

# Web Application

For researchers who prefer a graphical interface, an interactive web version is available.

Web Application: https://www.pepkio.com/tools/distrogene-probability-calculator

The web application includes interactive parameter sliders, distribution curve visualizations, step-by-step dilution worksheets, plate layout generators, shareable run permalinks, and publication-ready Methods text generation.

# Documentation and Resources

* GitHub Repository: https://github.com/pepkio/pepkio-distrogene-probability-calculator
* Web Application: https://www.pepkio.com/tools/distrogene-probability-calculator
* Source and issues: https://github.com/pepkio/pepkio-distrogene-probability-calculator/issues

# About Pepkio

Pepkio (https://www.pepkio.com/) develops software tools and bioinformatics solutions for life science researchers, including laboratory calculators and analysis services (https://www.pepkio.com/cro). See https://www.pepkio.com for additional tools and services.

# Keywords

* genomics
* probability calculator
* CRISPR library coverage
* sgRNA representation
* hypergeometric test
* gene ontology enrichment
* pathway overrepresentation
* variant detection
* allele frequency
* UMI barcode collision
* single cell rna sequencing
* occupancy distribution
* serial dilution
* standard curve
* qPCR setup
* ELISA assay
* concentration calculator
* statistical genetics
* Poisson distribution
* binomial distribution
* negative binomial distribution
* bioinformatics tools
* sequencing depth
* model organisms
* CRISPR screen guide coverage calculator
* hypergeometric gene enrichment analysis
* low frequency variant detection probability
* unique molecular identifier barcode collision
* single cell droplet barcode collision rate
* quantitative PCR serial dilution series planner
* standard curve calculation for ELISA assay
* reverse power calculation for sequencing depth
* Poisson sampling model for pooled CRISPR libraries
* cumulative tail probability calculation in genomics
* Fisher exact test pathway enrichment tool
* bioinformatics python client for probability modeling
* next generation sequencing depth optimization
* model organism gene population background presets
* overdispersed sequencing library probability distribution
* laboratory reagent dilution and concentration solver
