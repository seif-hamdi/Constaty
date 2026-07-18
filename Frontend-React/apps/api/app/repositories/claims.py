"""In-memory claim store for Phase 1. Will be replaced by Supabase/SQLite later."""
from __future__ import annotations
from app.schemas.claim import Claim

store: dict[str, Claim] = {}


def get(claim_id: str) -> Claim | None:
    return store.get(claim_id)


def save(claim: Claim) -> None:
    store[claim.id] = claim