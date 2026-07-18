"""Transcription service — wraps Gemini audio transcription with fallback."""
from __future__ import annotations
import logging

from app.services import gemini_client

logger = logging.getLogger(__name__)


def transcribe(audio_path: str, language: str = "fr") -> dict:
    """Transcribe audio file. Returns dict with transcript, language, confidence.

    Falls back gracefully if Gemini is unavailable.
    """
    try:
        return gemini_client.transcribe_audio(audio_path, language)
    except gemini_client.GeminiUnavailable as e:
        logger.warning(f"Gemini unavailable for transcription: {e}")
        return {
            "transcript": "",
            "detected_language": language,
            "confidence": 0.0,
            "error": "TRANSCRIPTION_UNAVAILABLE",
        }
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        return {
            "transcript": "",
            "detected_language": language,
            "confidence": 0.0,
            "error": "TRANSCRIPTION_FAILED",
        }