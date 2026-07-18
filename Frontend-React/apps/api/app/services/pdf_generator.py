"""PDF generation service — fills the Tunisian constat by overlaying text
onto the static scanned template using ReportLab + pypdf.

The template is a scanned image PDF (no AcroForm fields).
We create a transparent overlay with text at mapped coordinates,
then merge it onto a copy of the original.
"""
from __future__ import annotations
import json
import logging
from pathlib import Path
from io import BytesIO

from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader, PdfWriter

from app.schemas.claim import Claim, YesNo

logger = logging.getLogger(__name__)

TEMPLATE_PATH = Path(__file__).resolve().parent.parent.parent.parent.parent / "data" / "templates" / "tunisian-constat.pdf"
FIELD_MAP_PATH = Path(__file__).resolve().parent.parent.parent.parent.parent / "data" / "templates" / "field-map.json"
OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent.parent / "storage" / "generated"


def _load_field_map() -> dict:
    with open(FIELD_MAP_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _get_claim_value(claim: Claim, field_id: str) -> str:
    """Extract a string value from the claim for a given field_id."""
    # Map field_id to claim attribute paths
    mapping = {
        "accident_date": lambda c: c.accident.date or "",
        "accident_time": lambda c: c.accident.time or "",
        "accident_location": lambda c: c.accident.location or "",
        "injured_persons": lambda c: c.accident.injured_persons.value if c.accident.injured_persons else "",
        "other_material_damage": lambda c: c.accident.other_material_damage.value if c.accident.other_material_damage else "",
        "witnesses": lambda c: c.accident.witnesses or "",

        # Vehicle A
        "vehicle_a_insurance_company": lambda c: c.vehicle_a.insurance_company or "",
        "vehicle_a_insurance_policy_no": lambda c: c.vehicle_a.insurance_policy_no or "",
        "vehicle_a_insurance_agency": lambda c: c.vehicle_a.insurance_agency or "",
        "vehicle_a_attestation_valid_from": lambda c: c.vehicle_a.attestation_valid_from or "",
        "vehicle_a_attestation_valid_to": lambda c: c.vehicle_a.attestation_valid_to or "",
        "vehicle_a_driver_name": lambda c: c.vehicle_a.driver_name or "",
        "vehicle_a_driver_firstname": lambda c: c.vehicle_a.driver_firstname or "",
        "vehicle_a_driver_address": lambda c: c.vehicle_a.driver_address or "",
        "vehicle_a_driver_license_no": lambda c: c.vehicle_a.driver_license_no or "",
        "vehicle_a_driver_license_delivery_date": lambda c: c.vehicle_a.driver_license_delivery_date or "",
        "vehicle_a_insured_name": lambda c: c.vehicle_a.insured_name or "",
        "vehicle_a_insured_firstname": lambda c: c.vehicle_a.insured_firstname or "",
        "vehicle_a_insured_address": lambda c: c.vehicle_a.insured_address or "",
        "vehicle_a_insured_phone": lambda c: c.vehicle_a.insured_phone or "",
        "vehicle_a_make_type": lambda c: c.vehicle_a.make_type or "",
        "vehicle_a_registration_no": lambda c: c.vehicle_a.registration_no or "",
        "vehicle_a_direction_from": lambda c: c.vehicle_a.direction_from or "",
        "vehicle_a_direction_to": lambda c: c.vehicle_a.direction_to or "",
        "vehicle_a_apparent_damage": lambda c: c.vehicle_a.apparent_damage or "",
        "vehicle_a_observations": lambda c: c.vehicle_a.observations or "",

        # Vehicle B
        "vehicle_b_insurance_company": lambda c: c.vehicle_b.insurance_company or "",
        "vehicle_b_insurance_policy_no": lambda c: c.vehicle_b.insurance_policy_no or "",
        "vehicle_b_insurance_agency": lambda c: c.vehicle_b.insurance_agency or "",
        "vehicle_b_attestation_valid_from": lambda c: c.vehicle_b.attestation_valid_from or "",
        "vehicle_b_attestation_valid_to": lambda c: c.vehicle_b.attestation_valid_to or "",
        "vehicle_b_driver_name": lambda c: c.vehicle_b.driver_name or "",
        "vehicle_b_driver_firstname": lambda c: c.vehicle_b.driver_firstname or "",
        "vehicle_b_driver_address": lambda c: c.vehicle_b.driver_address or "",
        "vehicle_b_driver_license_no": lambda c: c.vehicle_b.driver_license_no or "",
        "vehicle_b_driver_license_delivery_date": lambda c: c.vehicle_b.driver_license_delivery_date or "",
        "vehicle_b_insured_name": lambda c: c.vehicle_b.insured_name or "",
        "vehicle_b_insured_firstname": lambda c: c.vehicle_b.insured_firstname or "",
        "vehicle_b_insured_address": lambda c: c.vehicle_b.insured_address or "",
        "vehicle_b_insured_phone": lambda c: c.vehicle_b.insured_phone or "",
        "vehicle_b_make_type": lambda c: c.vehicle_b.make_type or "",
        "vehicle_b_registration_no": lambda c: c.vehicle_b.registration_no or "",
        "vehicle_b_direction_from": lambda c: c.vehicle_b.direction_from or "",
        "vehicle_b_direction_to": lambda c: c.vehicle_b.direction_to or "",
        "vehicle_b_apparent_damage": lambda c: c.vehicle_b.apparent_damage or "",
        "vehicle_b_observations": lambda c: c.vehicle_b.observations or "",

        # Page 2
        "insured_name_page2": lambda c: c.insured_detail.name or "",
        "insured_profession_page2": lambda c: c.insured_detail.profession or "",
        "insured_phone_page2": lambda c: c.insured_detail.phone or "",
        "accident_circumstances_description_page2": lambda c: c.insured_detail.circumstances_description or "",
        "police_report_established": lambda c: c.insured_detail.police_report_established.value if c.insured_detail.police_report_established else "",
        "police_report_exists": lambda c: c.insured_detail.police_report_exists.value if c.insured_detail.police_report_exists else "",
        "police_report_details": lambda c: c.insured_detail.police_report_details or "",
        "driver_is_habitual": lambda c: c.insured_detail.driver_is_habitual.value if c.insured_detail.driver_is_habitual else "",
        "driver_birth_date": lambda c: c.insured_detail.driver_birth_date or "",
        "driver_is_employee": lambda c: c.insured_detail.driver_is_employee.value if c.insured_detail.driver_is_employee else "",
        "driver_other_capacity": lambda c: c.insured_detail.driver_other_capacity or "",
        "vehicle_garage_location": lambda c: c.insured_detail.vehicle_garage_location or "",
        "vehicle_displacement_reason": lambda c: c.insured_detail.vehicle_displacement_reason or "",
        "damage_expertise_garage": lambda c: c.insured_detail.damage_expertise_garage or "",
        "damage_expertise_date": lambda c: c.insured_detail.damage_expertise_date or "",
        "damage_expertise_phone": lambda c: c.insured_detail.damage_expertise_phone or "",
    }

    getter = mapping.get(field_id)
    if getter:
        try:
            return getter(claim)
        except (AttributeError, TypeError):
            return ""
    return ""


def _wrap_text(text: str, max_width: float, font_name: str, font_size: float) -> list[str]:
    """Simple word-wrap for long text fields."""
    if not text:
        return []
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        # Rough character-based estimation (no stringWidth available here)
        if len(test) * font_size * 0.5 > max_width:
            if current:
                lines.append(current)
            current = word
        else:
            current = test
    if current:
        lines.append(current)
    return lines


def generate_constat_pdf(claim: Claim) -> str:
    """Generate a filled constat PDF for the given claim.

    Returns the file path to the generated PDF.
    """
    field_map = _load_field_map()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Create overlay
    overlay_buffer = BytesIO()
    page_size = field_map.get("pdf_page_size", {"width": 595, "height": 842})
    c = canvas.Canvas(overlay_buffer, pagesize=(page_size["width"], page_size["height"]))

    ink_color = Color(0.08, 0.13, 0.18)  # Dark ink, not pure black
    c.setFillColor(ink_color)

    pages = field_map.get("pages", {})

    # Page 1
    page1 = pages.get("1", {})
    c.setFont("Helvetica", 8)

    for field_id, coord in page1.items():
        if field_id.startswith("_") or field_id.startswith("circumstances_") or field_id.startswith("damage_diagram"):
            continue

        value = _get_claim_value(claim, field_id)
        if not value:
            continue

        x = coord.get("x", 0)
        y = coord.get("y", 0)
        font_size = coord.get("font_size", 8)
        max_width = coord.get("max_width", 200)
        ftype = coord.get("type", "text")

        c.setFont("Helvetica", font_size)

        if ftype == "checkbox_oui_non":
            # Place "X" next to the correct option
            if value.lower() in ("oui", "yes", "نعم"):
                c.drawString(x, y, "X  Oui")
            elif value.lower() in ("non", "no", "لا"):
                c.drawString(x + 40, y, "X  Non")
        else:
            # Wrap text if needed
            lines = _wrap_text(value, max_width, "Helvetica", font_size)
            for i, line in enumerate(lines):
                c.drawString(x, y - (i * (font_size + 2)), line)

    # Circumstances checkboxes
    circ_a = page1.get("circumstances_vehicle_a", {})
    circ_b = page1.get("circumstances_vehicle_b", {})
    if circ_a and claim.circumstances.vehicle_a:
        c.setFont("Helvetica", circ_a.get("font_size", 8))
        rows_y = circ_a.get("rows_start_y", 270)
        row_h = circ_a.get("row_height", 13)
        cols_x = circ_a.get("columns_start_x", [75])
        for num in claim.circumstances.vehicle_a:
            row_idx = (num - 1) if 1 <= num <= 17 else 0
            col_idx = 0  # First column for the X
            x = cols_x[col_idx] if col_idx < len(cols_x) else cols_x[0]
            y = rows_y - (row_idx * row_h)
            c.drawString(x, y, "X")

    if circ_b and claim.circumstances.vehicle_b:
        c.setFont("Helvetica", circ_b.get("font_size", 8))
        rows_y = circ_b.get("rows_start_y", 270)
        row_h = circ_b.get("row_height", 13)
        cols_x = circ_b.get("columns_start_x", [320])
        for num in claim.circumstances.vehicle_b:
            row_idx = (num - 1) if 1 <= num <= 17 else 0
            x = cols_x[0] if cols_x else 320
            y = rows_y - (row_idx * row_h)
            c.drawString(x, y, "X")

    # Circumstances total
    if claim.circumstances.total_checked is not None:
        total_coord = page1.get("circumstances_total_checked", {})
        if total_coord:
            c.setFont("Helvetica", total_coord.get("font_size", 8))
            c.drawString(total_coord.get("x", 280), total_coord.get("y", 48), str(claim.circumstances.total_checked))

    # Damage diagram — mark impact zone
    if claim.damage_diagram.vehicle_a_impact_zone:
        diag_a = page1.get("damage_diagram_a", {})
        if diag_a:
            c.setFont("Helvetica-Bold", 10)
            c.drawString(diag_a.get("center_x", 120) - 20, diag_a.get("center_y", 220) + 30, claim.damage_diagram.vehicle_a_impact_zone.value)

    if claim.damage_diagram.vehicle_b_impact_zone:
        diag_b = page1.get("damage_diagram_b", {})
        if diag_b:
            c.setFont("Helvetica-Bold", 10)
            c.drawString(diag_b.get("center_x", 380) - 20, diag_b.get("center_y", 220) + 30, claim.damage_diagram.vehicle_b_impact_zone.value)

    # Constaty note
    c.setFont("Helvetica-Oblique", 6)
    c.setFillColor(Color(0.4, 0.5, 0.6))
    c.drawString(200, 10, "Draft prepared with Constaty — review required")

    c.showPage()

    # Page 2
    page2 = pages.get("2", {})
    c.setFont("Helvetica", 8)
    c.setFillColor(ink_color)

    for field_id, coord in page2.items():
        if field_id.startswith("_"):
            continue

        value = _get_claim_value(claim, field_id)
        if not value:
            continue

        x = coord.get("x", 0)
        y = coord.get("y", 0)
        font_size = coord.get("font_size", 8)
        max_width = coord.get("max_width", 440)
        ftype = coord.get("type", "text")

        c.setFont("Helvetica", font_size)

        if ftype == "checkbox_oui_non":
            if value.lower() in ("oui", "yes"):
                c.drawString(x, y, "X  Oui")
            elif value.lower() in ("non", "no"):
                c.drawString(x + 40, y, "X  Non")
        else:
            lines = _wrap_text(value, max_width, "Helvetica", font_size)
            for i, line in enumerate(lines):
                c.drawString(x, y - (i * (font_size + 2)), line)

    # Constaty note page 2
    c.setFont("Helvetica-Oblique", 6)
    c.setFillColor(Color(0.4, 0.5, 0.6))
    c.drawString(200, 5, "Draft prepared with Constaty — review required")

    c.showPage()
    c.save()

    # Merge overlay with original template
    overlay_buffer.seek(0)
    overlay_reader = PdfReader(overlay_buffer)
    template_reader = PdfReader(str(TEMPLATE_PATH))
    writer = PdfWriter()

    for i, template_page in enumerate(template_reader.pages):
        if i < len(overlay_reader.pages):
            template_page.merge_page(overlay_reader.pages[i])
        writer.add_page(template_page)

    output_path = OUTPUT_DIR / f"constat_{claim.id}.pdf"
    with open(output_path, "wb") as f:
        writer.write(f)

    logger.info(f"Generated constat PDF: {output_path}")
    return str(output_path)