"""Damage analysis service — wraps Gemini VLM damage detection with fallback."""
from __future__ import annotations
import logging

from app.services import gemini_client

logger = logging.getLogger(__name__)


def analyze(image_path: str, vehicle: str = "A") -> dict:
    """Analyze vehicle damage from a photograph.

    Falls back to manual selection requirement if Gemini is unavailable.
    """
    try:
        return gemini_client.analyze_damage(image_path, vehicle)
    except gemini_client.GeminiUnavailable as e:
        logger.warning(f"Gemini unavailable for damage analysis: {e}")
        return {
            "damages": [],
            "image_quality": "unknown",
            "additional_images_required": True,
            "requires_physical_inspection": True,
            "overall_confidence": 0.0,
            "error": "AI_UNAVAILABLE",
        }
    except Exception as e:
        logger.error(f"Damage analysis failed: {e}")
        return {
            "damages": [],
            "image_quality": "unknown",
            "additional_images_required": True,
            "requires_physical_inspection": True,
            "overall_confidence": 0.0,
            "error": "ANALYSIS_FAILED",
        }