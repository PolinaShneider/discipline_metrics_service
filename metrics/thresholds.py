DEFAULT_THRESHOLDS = {
    "semantic_coherence": 0.5,
    "structural_balance": 0.6,
    "topic_flow": 0.3,
    "sequence_coverage": 0.6,
    "graph_coverage": 0.6,
    "redundancy": 0.4,
    "relevance": 0.5,
    "extra_topics_penalty": 0.4,
    "final_score": 0.6
}

def resolve_thresholds(overrides: dict | None = None) -> dict:
    if overrides is None:
        return DEFAULT_THRESHOLDS.copy()
    return {**DEFAULT_THRESHOLDS, **overrides}
