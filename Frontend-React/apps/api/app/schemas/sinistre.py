"""SinistrePackage — the handoff contract from Part 1 (driver) to Part 2 (insurer).

When a driver submits a claim, the backend creates a SinistrePackage that the
insurer-facing assessment platform can consume without parsing the frontend
or the generated PDF.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field


class CompletenessInfo(BaseModel):
    score: int = Field(ge=0, le=100, description="0-100 completeness score")
    missing_fields: list[str] = Field(default_factory=list)
    uncertain_fields: list[str] = Field(default_factory=list)


class ConsistencyInfo(BaseModel):
    score: Optional[int] = Field(default=None, ge=0, le=100)
    issues: list[dict] = Field(default_factory=list)


class AssessmentStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class DamageAssessmentRef(BaseModel):
    """Placeholder — Part 2 will populate this with CrewAI results."""
    damaged_components: list[dict] = Field(default_factory=list)
    consistency_report: Optional[dict] = None
    ai_confidence: Optional[float] = None


class CostEstimateRef(BaseModel):
    """Placeholder — Part 2 will populate this."""
    currency: str = "TND"
    minimum: Optional[float] = None
    expected: Optional[float] = None
    maximum: Optional[float] = None
    line_items: list[dict] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    confidence: Optional[float] = None


class SinistrePackage(BaseModel):
    schema_version: str = "1.0"
    sinistre_id: str
    claim_id: str
    submitted_at: Optional[datetime] = None
    claim: dict  # The full Claim object as dict
    constat_pdf_url: Optional[str] = None
    evidence: list[dict] = Field(default_factory=list)
    completeness: CompletenessInfo = Field(default_factory=CompletenessInfo)
    consistency: ConsistencyInfo = Field(default_factory=ConsistencyInfo)
    damage_assessment: Optional[DamageAssessmentRef] = None
    cost_estimate: Optional[CostEstimateRef] = None
    assessment_status: AssessmentStatus = AssessmentStatus.PENDING
    expert_review: Optional[dict] = None  # Part 2 will populate