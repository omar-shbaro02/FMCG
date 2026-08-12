"""Frozen leadership-output assembly and rendering."""

from app.domain.executive_outputs.generator import (
    FINAL_REVIEW_STATEMENT,
    OUTPUT_VERSION,
    ExecutiveOutputResult,
    generate_executive_output,
)

__all__ = [
    "FINAL_REVIEW_STATEMENT",
    "OUTPUT_VERSION",
    "ExecutiveOutputResult",
    "generate_executive_output",
]
