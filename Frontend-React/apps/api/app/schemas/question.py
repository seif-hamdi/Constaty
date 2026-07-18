"""UI-ready question model returned by the guided workflow."""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class QuestionOption(BaseModel):
    value: str
    label: str = ""
    label_translations: dict[str, str] = Field(default_factory=dict)


class Question(BaseModel):
    id: str
    section: str
    type: str  # date|text|choice|yes_no|time|location|voice|image_upload|document_upload|damage_selection|confirmation
    prompt: str
    prompt_translations: dict[str, str] = Field(default_factory=dict)
    required: bool = True
    options: list[QuestionOption] = Field(default_factory=list)
    help_text: Optional[str] = None
    help_translations: dict[str, str] = Field(default_factory=dict)