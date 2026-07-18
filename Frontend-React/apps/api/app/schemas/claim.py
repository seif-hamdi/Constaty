"""Canonical Claim model — the single source of truth for all claim data.

This schema is derived from the actual Tunisian constat PDF field inventory
(see docs/constat-field-inventory.md). The generated PDF is a rendering of
this model, not the other way around.
"""
from __future__ import annotations
from datetime import date, datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ClaimStatus(str, Enum):
    DRAFT = "DRAFT"
    COLLECTING = "COLLECTING"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    SUBMITTED = "SUBMITTED"
    ASSESSMENT_PENDING = "ASSESSMENT_PENDING"
    EXPERT_REVIEW = "EXPERT_REVIEW"
    CLOSED = "CLOSED"


class YesNo(str, Enum):
    OUI = "oui"
    NON = "non"


class Language(str, Enum):
    FR = "fr"
    AR = "ar"
    EN = "en"


class DamageZone(str, Enum):
    FRONT = "front"
    FRONT_LEFT = "front_left"
    FRONT_RIGHT = "front_right"
    REAR = "rear"
    REAR_LEFT = "rear_left"
    REAR_RIGHT = "rear_right"
    LEFT_SIDE = "left_side"
    RIGHT_SIDE = "right_side"
    WINDSHIELD = "windshield"
    ROOF = "roof"
    UNKNOWN = "unknown"


class DamageType(str, Enum):
    SCRATCH = "scratch"
    DENT = "dent"
    CRACK = "crack"
    BROKEN = "broken"
    DEFORMATION = "deformation"
    DETACHED = "detached"
    PAINT_DAMAGE = "paint_damage"
    UNKNOWN = "unknown"


class Severity(str, Enum):
    MINOR = "minor"
    MEDIUM = "medium"
    SEVERE = "severe"
    UNKNOWN = "unknown"


# -- Sub-models --

class AccidentInfo(BaseModel):
    date: Optional[str] = None
    time: Optional[str] = None
    location: Optional[str] = None
    injured_persons: Optional[YesNo] = None
    other_material_damage: Optional[YesNo] = None
    witnesses: Optional[str] = None


class VehicleInfo(BaseModel):
    # Insurance (section 6)
    insurance_company: Optional[str] = None
    insurance_policy_no: Optional[str] = None
    insurance_agency: Optional[str] = None
    attestation_valid_from: Optional[str] = None
    attestation_valid_to: Optional[str] = None
    # Driver (section 7)
    driver_name: Optional[str] = None
    driver_firstname: Optional[str] = None
    driver_address: Optional[str] = None
    driver_license_no: Optional[str] = None
    driver_license_delivery_date: Optional[str] = None
    # Insured (section 8)
    insured_name: Optional[str] = None
    insured_firstname: Optional[str] = None
    insured_address: Optional[str] = None
    insured_phone: Optional[str] = None
    # Vehicle (section 9)
    make_type: Optional[str] = None
    registration_no: Optional[str] = None
    direction_from: Optional[str] = None
    direction_to: Optional[str] = None
    # Damage (section 11)
    apparent_damage: Optional[str] = None
    # Observations (section 14)
    observations: Optional[str] = None


class Circumstances(BaseModel):
    """17 numbered circumstance checkboxes (see field inventory)."""
    vehicle_a: list[int] = Field(default_factory=list, description="List of circumstance numbers 1-17")
    vehicle_b: list[int] = Field(default_factory=list)
    total_checked: Optional[int] = None


class DamageDiagram(BaseModel):
    vehicle_a_impact_zone: Optional[DamageZone] = None
    vehicle_b_impact_zone: Optional[DamageZone] = None


class SketchInfo(BaseModel):
    description: Optional[str] = None
    image_url: Optional[str] = None


class InsuredDetail(BaseModel):
    name: Optional[str] = None
    profession: Optional[str] = None
    phone: Optional[str] = None
    circumstances_description: Optional[str] = None
    police_report_established: Optional[YesNo] = None
    police_report_exists: Optional[YesNo] = None
    police_report_details: Optional[str] = None
    driver_is_habitual: Optional[YesNo] = None
    driver_birth_date: Optional[str] = None
    driver_is_employee: Optional[YesNo] = None
    driver_other_capacity: Optional[str] = None
    vehicle_garage_location: Optional[str] = None
    vehicle_displacement_reason: Optional[str] = None
    damage_expertise_garage: Optional[str] = None
    damage_expertise_date: Optional[str] = None
    damage_expertise_phone: Optional[str] = None
    vehicle_stolen_details: Optional[str] = None
    vehicle_pledged_details: Optional[str] = None
    vehicle_heavy_load_weight: Optional[str] = None
    vehicle_towed_registration_no: Optional[str] = None
    vehicle_towed_total_weight: Optional[str] = None
    vehicle_towed_insurance_company: Optional[str] = None
    vehicle_towed_insurance_policy_no: Optional[str] = None
    other_material_damage_details: Optional[str] = None


class InjuredParty(BaseModel):
    name: Optional[str] = None
    firstname_age: Optional[str] = None
    address: Optional[str] = None
    profession: Optional[str] = None
    relationship: Optional[str] = None
    is_employee: Optional[YesNo] = None
    nature_severity: Optional[str] = None
    situation: Optional[str] = None
    first_aid_hospitalization: Optional[str] = None


class EvidenceRef(BaseModel):
    id: str
    type: str  # insurance_document, vehicle_registration, driver_license, damage_photo, scene_photo, audio
    url: Optional[str] = None
    vehicle: Optional[str] = None  # A or B
    metadata: dict = Field(default_factory=dict)


class DetectedDamage(BaseModel):
    zone: DamageZone
    part: Optional[str] = None
    damage_type: Optional[DamageType] = None
    severity: Optional[Severity] = None
    confidence: Optional[float] = None
    evidence_ids: list[str] = Field(default_factory=list)
    confirmed_by_user: bool = False
    requires_more_photos: bool = False
    requires_physical_inspection: bool = False


class ValidationIssue(BaseModel):
    code: str
    severity: str  # blocking, warning, info
    message: str
    field_path: Optional[str] = None
    recommended_question: Optional[str] = None


# -- Main Claim model --

class Claim(BaseModel):
    id: str
    public_token: Optional[str] = None
    status: ClaimStatus = ClaimStatus.DRAFT
    language: Language = Language.FR
    clarification_count: int = 0
    max_clarifications: int = 3

    accident: AccidentInfo = Field(default_factory=AccidentInfo)
    vehicle_a: VehicleInfo = Field(default_factory=VehicleInfo)
    vehicle_b: VehicleInfo = Field(default_factory=VehicleInfo)
    circumstances: Circumstances = Field(default_factory=Circumstances)
    damage_diagram: DamageDiagram = Field(default_factory=DamageDiagram)
    sketch: SketchInfo = Field(default_factory=SketchInfo)
    insured_detail: InsuredDetail = Field(default_factory=InsuredDetail)
    injured_party: InjuredParty = Field(default_factory=InjuredParty)

    narrative: Optional[str] = None
    narrative_normalized: Optional[str] = None
    detected_damage: list[DetectedDamage] = Field(default_factory=list)
    evidence: list[EvidenceRef] = Field(default_factory=list)

    missing_fields: list[str] = Field(default_factory=list)
    validation_issues: list[ValidationIssue] = Field(default_factory=list)

    field_confidences: dict[str, float] = Field(default_factory=dict)
    field_sources: dict[str, str] = Field(default_factory=dict)
    field_confirmations: dict[str, bool] = Field(default_factory=dict)

    constat_pdf_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None


# -- Mandatory fields list (derived from field inventory) --

MANDATORY_FIELDS = [
    "accident.date", "accident.time", "accident.location",
    "accident.injured_persons", "accident.other_material_damage",
    # Vehicle A
    "vehicle_a.insurance_company", "vehicle_a.insurance_policy_no", "vehicle_a.insurance_agency",
    "vehicle_a.attestation_valid_from", "vehicle_a.attestation_valid_to",
    "vehicle_a.driver_name", "vehicle_a.driver_firstname", "vehicle_a.driver_address",
    "vehicle_a.driver_license_no", "vehicle_a.driver_license_delivery_date",
    "vehicle_a.insured_name", "vehicle_a.insured_firstname", "vehicle_a.insured_address",
    "vehicle_a.make_type", "vehicle_a.registration_no",
    "vehicle_a.direction_from", "vehicle_a.direction_to",
    "vehicle_a.apparent_damage",
    # Vehicle B
    "vehicle_b.insurance_company", "vehicle_b.insurance_policy_no", "vehicle_b.insurance_agency",
    "vehicle_b.attestation_valid_from", "vehicle_b.attestation_valid_to",
    "vehicle_b.driver_name", "vehicle_b.driver_firstname", "vehicle_b.driver_address",
    "vehicle_b.driver_license_no", "vehicle_b.driver_license_delivery_date",
    "vehicle_b.insured_name", "vehicle_b.insured_firstname", "vehicle_b.insured_address",
    "vehicle_b.make_type", "vehicle_b.registration_no",
    "vehicle_b.direction_from", "vehicle_b.direction_to",
    "vehicle_b.apparent_damage",
    # Page 2
    "insured_detail.name", "insured_detail.circumstances_description",
    "insured_detail.police_report_established", "insured_detail.police_report_exists",
    "insured_detail.driver_is_habitual", "insured_detail.driver_birth_date",
    "insured_detail.driver_is_employee",
    "insured_detail.vehicle_garage_location", "insured_detail.vehicle_displacement_reason",
    "insured_detail.damage_expertise.garage",
]