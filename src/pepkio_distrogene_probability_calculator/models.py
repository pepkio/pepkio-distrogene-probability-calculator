# SPDX-License-Identifier: MIT
"""Data models for pepkio-distrogene-probability-calculator."""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class RunOptions(BaseModel):
    """Execution options for running a Pepkio tool."""

    idempotency_key: Optional[str] = None
    label: Optional[str] = None
    share: Optional[bool] = None


class RunResult(BaseModel):
    """Result of running a Pepkio tool."""

    run_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[Any] = None
    result_url: Optional[str] = None
    permalink: Optional[str] = None
    duration_ms: Optional[int] = None
    created_at: Optional[str] = None
    artifacts: Optional[List[Dict[str, Any]]] = None
    tool_id: Optional[str] = None
    label: Optional[str] = None

    def raise_for_error(self) -> None:
        """Raise PepkioRunError if run status is failed or error field is populated."""
        if self.status == "failed" or self.error:
            from .exceptions import PepkioRunError

            raise PepkioRunError(self.run_id, self.error or f"Run status is '{self.status}'")


class ManifestExample(BaseModel):
    """Example from tool manifest."""

    name: str
    input: Dict[str, Any]
    output: Optional[Dict[str, Any]] = None


class ToolManifest(BaseModel):
    """Tool manifest schema."""

    schema_version: Optional[str] = None
    tool_id: str
    title: str
    description: str
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    execution_mode: Optional[str] = None
    estimated_runtime_sec: Optional[float] = None
    input: Optional[Dict[str, Any]] = None
    output: Optional[Dict[str, Any]] = None
    agent_notes: Optional[str] = None
    example_prompts: Optional[List[str]] = None
    examples: List[Dict[str, Any]] = Field(default_factory=list)
    limits: Optional[Dict[str, Any]] = None
    input_schema: Optional[Dict[str, Any]] = None


# Helper typed input models for common scenarios
ScenarioType = Literal[
    "crispr_coverage",
    "go_enrichment",
    "variant_detection",
    "barcode_collision",
    "overdispersed_library",
    "custom",
]
ModeType = Literal["forward", "reverse"]
TailType = Literal["eq", "ge", "gt", "le", "lt"]
PopulationPresetType = Literal[
    "human_genome",
    "mouse_genome",
    "fly_genome",
    "worm_genome",
    "yeast_genome",
    "arabidopsis_genome",
    "custom",
]


class CrisprCoverageInput(BaseModel):
    """Input parameters for CRISPR coverage scenario."""

    scenario: Literal["crispr_coverage"] = "crispr_coverage"
    mode: ModeType = "forward"
    tail: TailType = "ge"
    library_size: int
    total_reads: int
    threshold_k: int = 1
    reads_per_guide: Optional[float] = None


class GoEnrichmentInput(BaseModel):
    """Input parameters for GO enrichment scenario."""

    scenario: Literal["go_enrichment"] = "go_enrichment"
    mode: ModeType = "forward"
    tail: TailType = "ge"
    population_preset: PopulationPresetType = "human_genome"
    population_N: Optional[int] = None
    pathway_size: int
    query_set_size: int
    overlap_count: int


class VariantDetectionInput(BaseModel):
    """Input parameters for variant detection scenario."""

    scenario: Literal["variant_detection"] = "variant_detection"
    mode: ModeType = "forward"
    tail: TailType = "ge"
    sequencing_reads: int
    allele_frequency: float
    variant_reads: int = 1
