"""Gemini AI client — central service for all Gemini calls.

Handles:
- Audio transcription
- Document/image structured extraction
- Damage analysis
- Retries with exponential backoff
- Structured Pydantic outputs
- Graceful failure with fallbacks

Never expose the API key. All calls happen server-side only.
"""
from __future__ import annotations
import os
import time
import json
import logging
from typing import Optional, Type, TypeVar
from pathlib import Path

from pydantic import BaseModel
from google import genai
from google.genai import types as gtypes

from app.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

# Retry config
MAX_RETRIES = 3
INITIAL_BACKOFF = 1.0
JITTER = 0.3


class GeminiUnavailable(Exception):
    """Raised when Gemini is not configured or repeatedly unavailable."""
    pass


def _get_client() -> genai.Client:
    key = settings.gemini_api_key
    if not key:
        raise GeminiUnavailable("GEMINI_API_KEY not configured")
    return genai.Client(api_key=key)


def _retry(fn):
    """Decorator: exponential backoff with jitter for Gemini calls."""
    def wrapper(*args, **kwargs):
        last_err = None
        for attempt in range(MAX_RETRIES):
            try:
                return fn(*args, **kwargs)
            except GeminiUnavailable:
                raise
            except Exception as e:
                last_err = e
                err_str = str(e).lower()
                # Don't retry on 404 (model not found) or 400 (bad request)
                if "404" in err_str or "400" in err_str or "not_found" in err_str:
                    raise
                if attempt < MAX_RETRIES - 1:
                    backoff = INITIAL_BACKOFF * (2 ** attempt) + JITTER
                    logger.warning(f"Gemini attempt {attempt+1} failed: {e}. Retrying in {backoff:.1f}s...")
                    time.sleep(backoff)
        raise last_err or GeminiUnavailable("Gemini repeatedly unavailable")
    return wrapper


@_retry
def transcribe_audio(audio_path: str, language_hint: str = "fr") -> dict:
    """Transcribe an audio file using Gemini.

    Returns: {"transcript": str, "detected_language": str, "confidence": float}
    """
    client = _get_client()
    model = settings.gemini_fast_model or "gemini-2.5-flash"

    f = client.files.upload(file=audio_path)

    lang_instruction = {
        "fr": "Transcribe in French.",
        "ar": "Transcribe in Arabic. If the speaker uses Tunisian dialect, transcribe phonetically in Arabic script.",
        "en": "Transcribe in English.",
    }.get(language_hint, "Transcribe accurately.")

    prompt = f"""{lang_instruction}
Return ONLY valid JSON:
{{"transcript": "...", "detected_language": "fr|ar|en|tn", "confidence": 0.0-1.0}}"""

    resp = client.models.generate_content(
        model=model,
        contents=[prompt, f],
        config=gtypes.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1,
        ),
    )

    try:
        data = json.loads(resp.text)
        return {
            "transcript": data.get("transcript", ""),
            "detected_language": data.get("detected_language", language_hint),
            "confidence": float(data.get("confidence", 0.7)),
        }
    except (json.JSONDecodeError, ValueError):
        return {"transcript": resp.text or "", "detected_language": language_hint, "confidence": 0.5}


@_retry
def extract_document(image_path: str, doc_type: str = "auto") -> dict:
    """Extract structured fields from a document image using Gemini VLM.

    Returns extracted fields dict with confidence scores.
    """
    client = _get_client()
    model = settings.gemini_fast_model or "gemini-2.5-flash"

    f = client.files.upload(file=image_path)

    prompt = f"""You are inspecting a Tunisian vehicle document (type: {doc_type}).
Extract all visible information accurately. If a field is not visible or unclear, use null.

Return ONLY valid JSON:
{{
  "extracted_fields": {{
    "insurance_company": null,
    "insurance_policy_no": null,
    "insurance_agency": null,
    "attestation_valid_from": null,
    "attestation_valid_to": null,
    "make_type": null,
    "registration_no": null,
    "insured_name": null,
    "insured_firstname": null,
    "insured_address": null,
    "insured_phone": null,
    "driver_name": null,
    "driver_firstname": null,
    "driver_license_no": null,
    "driver_license_delivery_date": null
  }},
  "document_type": "insurance_certificate|vehicle_registration|driver_license|unknown",
  "confidence": 0.0-1.0,
  "issues": []
}}"""

    resp = client.models.generate_content(
        model=model,
        contents=[prompt, f],
        config=gtypes.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1,
        ),
    )

    try:
        return json.loads(resp.text)
    except (json.JSONDecodeError, ValueError):
        return {"extracted_fields": {}, "document_type": "unknown", "confidence": 0.0, "issues": ["parse_error"]}


@_retry
def analyze_damage(image_path: str, vehicle: str = "A") -> dict:
    """Analyze vehicle damage from a photograph using Gemini VLM.

    Returns damage assessment with zones, types, severity, and confidence.
    """
    client = _get_client()
    model = settings.gemini_fast_model or "gemini-2.5-flash"

    f = client.files.upload(file=image_path)

    prompt = f"""You are a vehicle damage assessor. Analyze this photo of vehicle {vehicle}.
Identify the damaged area and type of damage.

Damage zones: front, front_left, front_right, rear, rear_left, rear_right, left_side, right_side, windshield, roof, unknown
Damage types: scratch, dent, crack, broken, deformation, detached, paint_damage, unknown
Severity: minor, medium, severe, unknown

Return ONLY valid JSON:
{{
  "damages": [
    {{
      "zone": "front_right",
      "part": "front_bumper",
      "damage_type": "dent",
      "severity": "medium",
      "confidence": 0.0-1.0
    }}
  ],
  "image_quality": "good|acceptable|poor",
  "additional_images_required": false,
  "requires_physical_inspection": false,
  "overall_confidence": 0.0-1.0
}}

If no damage is visible, return empty damages array with image_quality assessment."""

    resp = client.models.generate_content(
        model=model,
        contents=[prompt, f],
        config=gtypes.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1,
        ),
    )

    try:
        return json.loads(resp.text)
    except (json.JSONDecodeError, ValueError):
        return {
            "damages": [],
            "image_quality": "unknown",
            "additional_images_required": True,
            "requires_physical_inspection": True,
            "overall_confidence": 0.0,
        }