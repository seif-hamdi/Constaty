"""Predefined question catalogue derived from the Tunisian constat PDF field inventory.

Each question maps to a canonical Claim field path. Questions are ordered
by the natural flow of accident reporting, grouped by section.

The catalogue covers all 51 mandatory fields plus key optional fields.
"""
from __future__ import annotations
from app.schemas.question import Question, QuestionOption
from app.schemas.claim import Language

# ── Helpers ──

def _q(
    qid: str,
    section: str,
    qtype: str,
    prompt_fr: str,
    prompt_ar: str,
    prompt_en: str,
    field_path: str,
    required: bool = True,
    help_fr: str = "",
    help_ar: str = "",
    help_en: str = "",
    options: list[QuestionOption] | None = None,
) -> dict:
    return {
        "id": qid,
        "section": section,
        "type": qtype,
        "field_path": field_path,
        "required": required,
        "prompt": prompt_fr,
        "prompt_translations": {"fr": prompt_fr, "ar": prompt_ar, "en": prompt_en},
        "help_text": help_fr or None,
        "help_translations": {"fr": help_fr, "ar": help_ar, "en": help_en} if help_fr else {},
        "options": [o.model_dump() for o in options] if options else [],
    }


_OUI_NON = [
    QuestionOption(value="oui", label="Oui", label_translations={"fr": "Oui", "ar": "نعم", "en": "Yes"}),
    QuestionOption(value="non", label="Non", label_translations={"fr": "Non", "ar": "لا", "en": "No"}),
]

# ── Section 1: Accident info ──
ACCIDENT_QUESTIONS = [
    _q("accident_date", "accident", "date",
       "Quand s'est-il produit l'accident ?", "متى وقع الحادث؟", "When did the accident happen?",
       "accident.date"),
    _q("accident_time", "accident", "time",
       "À quelle heure ?", "في أي ساعة؟", "At what time?",
       "accident.time"),
    _q("accident_location", "accident", "location",
       "Où s'est-il produit l'accident ? (lieu)", "أين وقع الحادث؟ (المكان)", "Where did the accident happen?",
       "accident.location",
       help_fr="Indiquez la rue, la ville ou un point de repère.",
       help_ar="حدد الشارع، المدينة أو نقطة مرجعية.",
       help_en="Enter the street, city or a landmark."),
    _q("injured_persons", "accident", "yes_no",
       "Y a-t-il des blessés, même légers ?", "هل هناك جرحى، ولو بسيطين؟", "Are there any injuries, even minor?",
       "accident.injured_persons",
       options=_OUI_NON),
    _q("other_material_damage", "accident", "yes_no",
       "Y a-t-il des dégâts matériels autres qu'aux véhicules A et B ?",
       "هل هناك أضرار مادية غير المركبتين A و B؟",
       "Is there material damage other than to vehicles A and B?",
       "accident.other_material_damage",
       options=_OUI_NON),
    _q("witnesses", "accident", "text",
       "Y a-t-il des témoins ? (noms, adresses, téléphones)",
       "هل هناك شهود؟ (الأسماء، العناوين، الهواتف)",
       "Are there witnesses? (names, addresses, phones)",
       "accident.witnesses",
       required=False),
]

# ── Section 2: Vehicle A ──
VEHICLE_A_QUESTIONS = [
    _q("vehicle_a_insurance_company", "vehicle_a", "text",
       "Véhicule A — Par quelle société est-il assuré ?",
       "المركبة A — بأي شركة مؤمنة؟",
       "Vehicle A — Which insurance company?",
       "vehicle_a.insurance_company"),
    _q("vehicle_a_insurance_policy_no", "vehicle_a", "text",
       "Véhicule A — Numéro de police d'assurance ?",
       "المركبة A — رقم وثيقة التأمين؟",
       "Vehicle A — Insurance policy number?",
       "vehicle_a.insurance_policy_no"),
    _q("vehicle_a_insurance_agency", "vehicle_a", "text",
       "Véhicule A — Agence ?",
       "المركبة A — الوكالة؟",
       "Vehicle A — Agency?",
       "vehicle_a.insurance_agency"),
    _q("vehicle_a_attestation_valid_from", "vehicle_a", "date",
       "Véhicule A — Attestation valable du ?",
       "المركبة A — الوثيقة سارية من؟",
       "Vehicle A — Attestation valid from?",
       "vehicle_a.attestation_valid_from"),
    _q("vehicle_a_attestation_valid_to", "vehicle_a", "date",
       "Véhicule A — Jusqu'au ?",
       "المركبة A — إلى؟",
       "Vehicle A — Valid until?",
       "vehicle_a.attestation_valid_to"),
    _q("vehicle_a_driver_name", "vehicle_a", "text",
       "Véhicule A — Nom du conducteur ?",
       "المركبة A — لقب السائق؟",
       "Vehicle A — Driver's last name?",
       "vehicle_a.driver_name"),
    _q("vehicle_a_driver_firstname", "vehicle_a", "text",
       "Véhicule A — Prénom du conducteur ?",
       "المركبة A — اسم السائق؟",
       "Vehicle A — Driver's first name?",
       "vehicle_a.driver_firstname"),
    _q("vehicle_a_driver_address", "vehicle_a", "text",
       "Véhicule A — Adresse du conducteur ?",
       "المركبة A — عنوان السائق؟",
       "Vehicle A — Driver's address?",
       "vehicle_a.driver_address"),
    _q("vehicle_a_driver_license_no", "vehicle_a", "text",
       "Véhicule A — Numéro de permis de conduire ?",
       "المركبة A — رقم رخصة القيادة؟",
       "Vehicle A — Driver's license number?",
       "vehicle_a.driver_license_no"),
    _q("vehicle_a_driver_license_delivery_date", "vehicle_a", "date",
       "Véhicule A — Permis délivré le ?",
       "المركبة A — رخصة تسلمت في؟",
       "Vehicle A — License issued on?",
       "vehicle_a.driver_license_delivery_date"),
    _q("vehicle_a_insured_name", "vehicle_a", "text",
       "Véhicule A — Nom de l'assuré ?",
       "المركبة A — لقب المؤمَّن؟",
       "Vehicle A — Insured's last name?",
       "vehicle_a.insured_name"),
    _q("vehicle_a_insured_firstname", "vehicle_a", "text",
       "Véhicule A — Prénom de l'assuré ?",
       "المركبة A — اسم المؤمَّن؟",
       "Vehicle A — Insured's first name?",
       "vehicle_a.insured_firstname"),
    _q("vehicle_a_insured_address", "vehicle_a", "text",
       "Véhicule A — Adresse de l'assuré ?",
       "المركبة A — عنوان المؤمَّن؟",
       "Vehicle A — Insured's address?",
       "vehicle_a.insured_address"),
    _q("vehicle_a_insured_phone", "vehicle_a", "text",
       "Véhicule A — Téléphone de l'assuré ?",
       "المركبة A — هاتف المؤمَّن؟",
       "Vehicle A — Insured's phone?",
       "vehicle_a.insured_phone",
       required=False),
    _q("vehicle_a_make_type", "vehicle_a", "text",
       "Véhicule A — Marque et type ?",
       "المركبة A — العلامة والطراز؟",
       "Vehicle A — Make and type?",
       "vehicle_a.make_type"),
    _q("vehicle_a_registration_no", "vehicle_a", "text",
       "Véhicule A — Numéro d'immatriculation ?",
       "المركبة A — رقم التسجيل؟",
       "Vehicle A — Registration number?",
       "vehicle_a.registration_no"),
    _q("vehicle_a_direction_from", "vehicle_a", "text",
       "Véhicule A — Sens suivi. Venant de ?",
       "المركبة A — الاتجاه. قادم من؟",
       "Vehicle A — Direction. Coming from?",
       "vehicle_a.direction_from"),
    _q("vehicle_a_direction_to", "vehicle_a", "text",
       "Véhicule A — Allant à ?",
       "المركبة A — متجه إلى؟",
       "Vehicle A — Going to?",
       "vehicle_a.direction_to"),
    _q("vehicle_a_apparent_damage", "vehicle_a", "text",
       "Véhicule A — Dégâts apparents ?",
       "المركبة A — الأضرار الظاهرة؟",
       "Vehicle A — Apparent damage?",
       "vehicle_a.apparent_damage",
       help_fr="Décrivez les dégâts visibles sur votre véhicule.",
       help_ar="صف الأضرار المرئية على مركبتك.",
       help_en="Describe the visible damage on your vehicle."),
    _q("vehicle_a_observations", "vehicle_a", "text",
       "Véhicule A — Observations ?",
       "المركبة A — ملاحظات؟",
       "Vehicle A — Observations?",
       "vehicle_a.observations",
       required=False),
]

# ── Section 3: Vehicle B ──
VEHICLE_B_QUESTIONS = [
    _q("vehicle_b_insurance_company", "vehicle_b", "text",
       "Véhicule B — Par quelle société est-il assuré ?",
       "المركبة B — بأي شركة مؤمنة؟",
       "Vehicle B — Which insurance company?",
       "vehicle_b.insurance_company"),
    _q("vehicle_b_insurance_policy_no", "vehicle_b", "text",
       "Véhicule B — Numéro de police d'assurance ?",
       "المركبة B — رقم وثيقة التأمين؟",
       "Vehicle B — Insurance policy number?",
       "vehicle_b.insurance_policy_no"),
    _q("vehicle_b_insurance_agency", "vehicle_b", "text",
       "Véhicule B — Agence ?",
       "المركبة B — الوكالة؟",
       "Vehicle B — Agency?",
       "vehicle_b.insurance_agency"),
    _q("vehicle_b_attestation_valid_from", "vehicle_b", "date",
       "Véhicule B — Attestation valable du ?",
       "المركبة B — الوثيقة سارية من؟",
       "Vehicle B — Attestation valid from?",
       "vehicle_b.attestation_valid_from"),
    _q("vehicle_b_attestation_valid_to", "vehicle_b", "date",
       "Véhicule B — Jusqu'au ?",
       "المركبة B — إلى؟",
       "Vehicle B — Valid until?",
       "vehicle_b.attestation_valid_to"),
    _q("vehicle_b_driver_name", "vehicle_b", "text",
       "Véhicule B — Nom du conducteur ?",
       "المركبة B — لقب السائق؟",
       "Vehicle B — Driver's last name?",
       "vehicle_b.driver_name"),
    _q("vehicle_b_driver_firstname", "vehicle_b", "text",
       "Véhicule B — Prénom du conducteur ?",
       "المركبة B — اسم السائق؟",
       "Vehicle B — Driver's first name?",
       "vehicle_b.driver_firstname"),
    _q("vehicle_b_driver_address", "vehicle_b", "text",
       "Véhicule B — Adresse du conducteur ?",
       "المركبة B — عنوان السائق؟",
       "Vehicle B — Driver's address?",
       "vehicle_b.driver_address"),
    _q("vehicle_b_driver_license_no", "vehicle_b", "text",
       "Véhicule B — Numéro de permis de conduire ?",
       "المركبة B — رقم رخصة القيادة؟",
       "Vehicle B — Driver's license number?",
       "vehicle_b.driver_license_no"),
    _q("vehicle_b_driver_license_delivery_date", "vehicle_b", "date",
       "Véhicule B — Permis délivré le ?",
       "المركبة B — رخصة تسلمت في؟",
       "Vehicle B — License issued on?",
       "vehicle_b.driver_license_delivery_date"),
    _q("vehicle_b_insured_name", "vehicle_b", "text",
       "Véhicule B — Nom de l'assuré ?",
       "المركبة B — لقب المؤمَّن؟",
       "Vehicle B — Insured's last name?",
       "vehicle_b.insured_name"),
    _q("vehicle_b_insured_firstname", "vehicle_b", "text",
       "Véhicule B — Prénom de l'assuré ?",
       "المركبة B — اسم المؤمَّن؟",
       "Vehicle B — Insured's first name?",
       "vehicle_b.insured_firstname"),
    _q("vehicle_b_insured_address", "vehicle_b", "text",
       "Véhicule B — Adresse de l'assuré ?",
       "المركبة B — عنوان المؤمَّن؟",
       "Vehicle B — Insured's address?",
       "vehicle_b.insured_address"),
    _q("vehicle_b_insured_phone", "vehicle_b", "text",
       "Véhicule B — Téléphone de l'assuré ?",
       "المركبة B — هاتف المؤمَّن؟",
       "Vehicle B — Insured's phone?",
       "vehicle_b.insured_phone",
       required=False),
    _q("vehicle_b_make_type", "vehicle_b", "text",
       "Véhicule B — Marque et type ?",
       "المركبة B — العلامة والطراز؟",
       "Vehicle B — Make and type?",
       "vehicle_b.make_type"),
    _q("vehicle_b_registration_no", "vehicle_b", "text",
       "Véhicule B — Numéro d'immatriculation ?",
       "المركبة B — رقم التسجيل؟",
       "Vehicle B — Registration number?",
       "vehicle_b.registration_no"),
    _q("vehicle_b_direction_from", "vehicle_b", "text",
       "Véhicule B — Sens suivi. Venant de ?",
       "المركبة B — الاتجاه. قادم من؟",
       "Vehicle B — Direction. Coming from?",
       "vehicle_b.direction_from"),
    _q("vehicle_b_direction_to", "vehicle_b", "text",
       "Véhicule B — Allant à ?",
       "المركبة B — متجه إلى؟",
       "Vehicle B — Going to?",
       "vehicle_b.direction_to"),
    _q("vehicle_b_apparent_damage", "vehicle_b", "text",
       "Véhicule B — Dégâts apparents ?",
       "المركبة B — الأضرار الظاهرة؟",
       "Vehicle B — Apparent damage?",
       "vehicle_b.apparent_damage"),
    _q("vehicle_b_observations", "vehicle_b", "text",
       "Véhicule B — Observations ?",
       "المركبة B — ملاحظات؟",
       "Vehicle B — Observations?",
       "vehicle_b.observations",
       required=False),
]

# ── Section 4: Page 2 details ──
DETAIL_QUESTIONS = [
    _q("insured_detail_name", "details", "text",
       "Nom de l'assuré (page 2) ?",
       "لقب المؤمَّن (الصفحة 2)؟",
       "Insured's name (page 2)?",
       "insured_detail.name"),
    _q("accident_circumstances_description", "details", "text",
       "Décrivez les circonstances de l'accident.",
       "صف ظروف الحادث.",
       "Describe the circumstances of the accident.",
       "insured_detail.circumstances_description",
       help_fr="Expliquez ce qui s'est passé dans vos propres mots.",
       help_ar="اشرح ما حدث بكلماتك الخاصة.",
       help_en="Explain what happened in your own words."),
    _q("police_report_established", "details", "yes_no",
       "Un procès-verbal de la Garde Nationale a-t-il été établi ?",
       "هل تم تحرير محضر من الحرس الوطني؟",
       "Was a National Guard report established?",
       "insured_detail.police_report_established",
       options=_OUI_NON),
    _q("police_report_exists", "details", "yes_no",
       "Y a-t-il un rapport de police ?",
       "هل يوجد تقرير شرطة؟",
       "Is there a police report?",
       "insured_detail.police_report_exists",
       options=_OUI_NON),
    _q("driver_is_habitual", "details", "yes_no",
       "Est-il le conducteur habituel du véhicule ?",
       "هل هو السائق المعتاد للمركبة؟",
       "Is he/she the habitual driver of the vehicle?",
       "insured_detail.driver_is_habitual",
       options=_OUI_NON),
    _q("driver_birth_date", "details", "date",
       "Date de naissance du conducteur ?",
       "تاريخ ميلاد السائق؟",
       "Driver's date of birth?",
       "insured_detail.driver_birth_date"),
    _q("driver_is_employee", "details", "yes_no",
       "Est-il salarié de l'assuré ?",
       "هل هو أجير المؤمَّن؟",
       "Is he/she an employee of the insured?",
       "insured_detail.driver_is_employee",
       options=_OUI_NON),
    _q("vehicle_garage_location", "details", "text",
       "Lieu habituel de garage du véhicule ?",
       "مكان المرآب المعتاد للمركبة؟",
       "Usual garage location of the vehicle?",
       "insured_detail.vehicle_garage_location"),
    _q("vehicle_displacement_reason", "details", "text",
       "Quel était le motif du déplacement ?",
       "ما كان سبب التنقل؟",
       "What was the reason for the trip?",
       "insured_detail.vehicle_displacement_reason"),
    _q("damage_expertise_garage", "details", "text",
       "Garage où le véhicule sera visible pour l'expertise ?",
       "المرآب الذي ستكون فيه المركبة مرئية للخبرة؟",
       "Garage where the vehicle can be inspected?",
       "insured_detail.damage_expertise.garage"),
]

# ── Full catalogue ──
ALL_QUESTIONS: list[dict] = (
    ACCIDENT_QUESTIONS
    + VEHICLE_A_QUESTIONS
    + VEHICLE_B_QUESTIONS
    + DETAIL_QUESTIONS
)

# Map question id → question dict
QUESTION_MAP: dict[str, dict] = {q["id"]: q for q in ALL_QUESTIONS}

# Ordered list of question ids
QUESTION_ORDER: list[str] = [q["id"] for q in ALL_QUESTIONS]

# Sections in order
SECTIONS = ["accident", "vehicle_a", "vehicle_b", "details", "review"]


def get_question(qid: str) -> dict | None:
    return QUESTION_MAP.get(qid)


def first_question_id() -> str:
    return QUESTION_ORDER[0]


def next_question_id(current_id: str) -> str | None:
    idx = QUESTION_ORDER.index(current_id) if current_id in QUESTION_MAP else -1
    next_idx = idx + 1
    if next_idx < len(QUESTION_ORDER):
        return QUESTION_ORDER[next_idx]
    return None


def section_for_question(qid: str) -> str:
    q = QUESTION_MAP.get(qid)
    return q["section"] if q else "unknown"


def section_index(section: str) -> int:
    try:
        return SECTIONS.index(section)
    except ValueError:
        return 0


def to_question(qid: str, lang: str = "fr") -> Question:
    """Convert a catalogue dict to a Question model (strips field_path)."""
    q = QUESTION_MAP[qid]
    return Question(
        id=q["id"],
        section=q["section"],
        type=q["type"],
        prompt=q["prompt_translations"].get(lang, q["prompt"]),
        prompt_translations=q["prompt_translations"],
        required=q["required"],
        options=[QuestionOption(**o) for o in q["options"]],
        help_text=q.get("help_text"),
        help_translations=q.get("help_translations", {}),
    )