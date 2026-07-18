"""Document extraction service — wraps Gemini VLM extraction with fallback."""
from __future__ import annotations
import logging

from app.services import gemini_client

logger = logging.getLogger(__name__)


def extract(image_path: str, doc_type: str = "auto") -> dict:
    """Extract structured fields from a document image.

    Falls back to empty extraction if Gemini is unavailable.
    """
    try:
        return gemini_client.extract_document(image_path, doc_type)
    except gemini_client.GeminiUnavailable as e:
        logger.warning(f"Gemini unavailable for document extraction: {e}")
        return {
            "extracted_fields": {},
            "document_type": "unknown",
            "confidence": 0.0,
            "issues": ["AI_UNAVAILABLE"],
        }
    except Exception as e:
        logger.error(f"Document extraction failed: {e}")
        return {
            "extracted_fields": {},
            "document_type": "unknown",
            "confidence": 0.0,
            "issues": ["EXTRACTION_FAILED"],
        }