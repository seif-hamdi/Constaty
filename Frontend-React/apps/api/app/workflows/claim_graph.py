"""LangGraph claim collection graph.

The graph controls the guided claim collection workflow:
    START → normalize → extract_and_merge → validate → choose_next → prepare_response → END

The graph is compiled with a MemorySaver checkpointer keyed by claim_id (thread_id),
so each claim can be resumed across multiple API calls.
"""
from __future__ import annotations

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.workflows.claim_state import GraphState
from app.workflows.nodes.claim_nodes import (
    normalize_input,
    extract_and_merge,
    validate,
    choose_next,
    prepare_response,
)


def _should_continue(state: GraphState) -> str:
    """Conditional edge after choose_next: continue or finish."""
    if state.get("finished"):
        return "prepare_response"
    return "prepare_response"


def build_claim_graph():
    """Build and compile the claim collection graph."""
    graph = StateGraph(GraphState)

    graph.add_node("normalize_input", normalize_input)
    graph.add_node("extract_and_merge", extract_and_merge)
    graph.add_node("validate", validate)
    graph.add_node("choose_next", choose_next)
    graph.add_node("prepare_response", prepare_response)

    graph.add_edge(START, "normalize_input")
    graph.add_edge("normalize_input", "extract_and_merge")
    graph.add_edge("extract_and_merge", "validate")
    graph.add_edge("validate", "choose_next")
    graph.add_edge("choose_next", "prepare_response")
    graph.add_edge("prepare_response", END)

    checkpointer = MemorySaver()
    return graph.compile(
        checkpointer=checkpointer,
        interrupt_before=[],  # No interrupts for now — human-in-the-loop via API
    )


# Singleton — shared across all requests
_claim_graph = None


def get_claim_graph():
    global _claim_graph
    if _claim_graph is None:
        _claim_graph = build_claim_graph()
    return _claim_graph