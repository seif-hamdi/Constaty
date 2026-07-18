from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Witness(StrictModel):
    full_name: str | None
    address: str | None
    phone_or_email: str | None


class InsuredPerson(StrictModel):
    last_name: str | None
    first_name: str | None
    address: str | None
    postal_code: str | None
    country: str | None
    phone_or_email: str | None


class VehicleInformation(StrictModel):
    make_and_model: str | None
    registration_number: str | None
    registration_country: str | None
    trailer_registration_number: str | None
    trailer_registration_country: str | None


class InsurerInformation(StrictModel):
    company: str | None
    policy_number: str | None
    green_card_number: str | None
    valid_from: str | None
    valid_to: str | None
    agency_name: str | None
    agency_address: str | None
    agency_country: str | None
    agency_phone_or_email: str | None
    vehicle_damage_covered: bool | None


class DriverInformation(StrictModel):
    last_name: str | None
    first_name: str | None
    birth_date: str | None
    address: str | None
    country: str | None
    phone_or_email: str | None
    licence_number: str | None
    licence_category: str | None
    licence_valid_until: str | None


class VehicleParty(StrictModel):
    insured: InsuredPerson
    vehicle: VehicleInformation
    insurer: InsurerInformation
    driver: DriverInformation
    initial_impact_point: str | None
    visible_damage: list[str]
    observations: str | None


class AccidentInformation(StrictModel):
    date: str | None
    time: str | None
    country: str | None
    exact_location: str | None
    injuries_even_minor: bool | None
    damage_to_other_vehicles: bool | None
    damage_to_other_property: bool | None
    witnesses: list[Witness]


CircumstanceCode = Literal[
    1, 2, 3, 4, 5, 6, 7, 8, 9,
    10, 11, 12, 13, 14, 15, 16, 17,
]


class Circumstances(StrictModel):
    vehicle_a_codes: list[CircumstanceCode]
    vehicle_b_codes: list[CircumstanceCode]
    sketch_description: str | None


class InjuredPerson(StrictModel):
    full_name: str | None
    contact: str | None
    injury_description: str | None
    transported_to: str | None


class AdditionalDeclaration(StrictModel):
    detailed_incident_description: str | None
    police_or_gendarmerie_report: bool | None
    report_reference_or_station: str | None
    vehicle_available_for_inspection_at: str | None
    injured_people: list[InjuredPerson]


class Evidence(StrictModel):
    user_statement: str
    image_path_or_url: str | None
    image_observations: list[str]
    facts_supported_by_image: list[str]
    facts_not_proven_by_image: list[str]


class DataQuality(StrictModel):
    missing_fields: list[str]
    uncertain_fields: list[str]
    contradictions: list[str]
    user_confirmed: bool


class Constat(StrictModel):
    accident: AccidentInformation
    vehicle_a: VehicleParty
    vehicle_b: VehicleParty
    circumstances: Circumstances
    additional_declaration: AdditionalDeclaration
    evidence: Evidence
    data_quality: DataQuality


class ConstatTaskOutput(StrictModel):
    constat: Constat
    follow_up_questions: list[str]
    ready_for_confirmation: bool
    summary_for_user: str


class BaremeTestResult(StrictModel):
    passed: bool
    expected_case_title: str
    expected_x_pct: int
    expected_y_pct: int
    received_x_pct: int
    received_y_pct: int
    matched_features: list[str]
    missing_features: list[str]
    notes: str


class RiskAnalysisOutput(StrictModel):
    predicted_case_no: int
    predicted_case_title: str
    responsibility_x_pct: int
    responsibility_y_pct: int
    detected_features: list[str]
    explanation: str
    bareme_test: BaremeTestResult
    risk_level: Literal["low", "medium", "high"]
    risk_indicators: list[str] = Field(min_length=3, max_length=3)
    supporting_evidence: list[str]
    risk_summary: str
