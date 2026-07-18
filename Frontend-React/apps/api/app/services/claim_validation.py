"""Claim validation and field-path utilities."""
from __future__ import annotations
import datetime
from app.schemas.claim import Claim, YesNo, MANDATORY_FIELDS


def get_field(claim: Claim, path: str):
    """Get a nested field value from a dot-separated path like 'accident.date'."""
    parts = path.split(".")
    obj = claim
    for p in parts:
        if obj is None:
            return None
        if hasattr(obj, p):
            obj = getattr(obj, p)
        elif isinstance(obj, dict):
            obj = obj.get(p)
        else:
            return None
    return obj


def set_field(claim: Claim, path: str, value) -> None:
    """Set a nested field value. Creates intermediate objects if needed."""
    parts = path.split(".")
    obj = claim
    for p in parts[:-1]:
        current = getattr(obj, p, None)
        if current is None:
            # Check if the attribute has a model factory
            field_info = type(obj).model_fields.get(p)
            if field_info and field_info.default_factory:
                current = field_info.default_factory()
            else:
                current = type(obj).model_fields[p].annotation()
            setattr(obj, p, current)
        obj = current
    setattr(obj, parts[-1], value)


def is_field_filled(claim: Claim, path: str) -> bool:
    val = get_field(claim, path)
    if val is None:
        return False
    if isinstance(val, str) and val.strip() == "":
        return False
    if isinstance(val, YesNo):
        return True
    return True


def missing_mandatory(claim: Claim) -> list[str]:
    return [f for f in MANDATORY_FIELDS if not is_field_filled(claim, f)]


def validate_claim(claim: Claim) -> list[dict]:
    """Run deterministic validation checks. Returns list of issues."""
    issues: list[dict] = []

    # 1. Missing mandatory fields
    for path in missing_mandatory(claim):
        issues.append({
            "code": "MISSING_FIELD",
            "severity": "blocking",
            "message": f"Champ obligatoire manquant: {path}",
            "field_path": path,
        })

    # 2. Future accident date
    acc_date = get_field(claim, "accident.date")
    if acc_date:
        try:
            d = datetime.date.fromisoformat(acc_date)
            if d > datetime.date.today():
                issues.append({
                    "code": "FUTURE_DATE",
                    "severity": "blocking",
                    "message": "La date de l'accident ne peut pas être dans le futur.",
                    "field_path": "accident.date",
                })
        except (ValueError, TypeError):
            issues.append({
                "code": "INVALID_DATE",
                "severity": "warning",
                "message": "Format de date invalide.",
                "field_path": "accident.date",
            })

    # 3. Vehicle A and B not identical
    reg_a = get_field(claim, "vehicle_a.registration_no")
    reg_b = get_field(claim, "vehicle_b.registration_no")
    if reg_a and reg_b and reg_a.strip().lower() == reg_b.strip().lower():
        issues.append({
            "code": "DUPLICATE_VEHICLE",
            "severity": "blocking",
            "message": "Les véhicules A et B ont le même numéro d'immatriculation.",
            "field_path": "vehicle_b.registration_no",
        })

    # 4. At least one damage description
    dmg_a = get_field(claim, "vehicle_a.apparent_damage")
    dmg_b = get_field(claim, "vehicle_b.apparent_damage")
    if not dmg_a and not dmg_b:
        issues.append({
            "code": "NO_DAMAGE_DESC",
            "severity": "warning",
            "message": "Aucun dégât apparent décrit pour les deux véhicules.",
        })

    return issues


def completeness_score(claim: Claim) -> int:
    """0-100 completeness score based on mandatory fields filled."""
    filled = sum(1 for f in MANDATORY_FIELDS if is_field_filled(claim, f))
    return int(filled / len(MANDATORY_FIELDS) * 100)


def ready_for_review(claim: Claim) -> bool:
    """Check if claim has all mandatory fields and no blocking issues."""
    if missing_mandatory(claim):
        return False
    for issue in validate_claim(claim):
        if issue["severity"] == "blocking":
            return False
    return True