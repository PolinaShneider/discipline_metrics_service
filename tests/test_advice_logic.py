from metrics.evaluation import generate_advice
from metrics.thresholds import resolve_thresholds


def test_advice_for_high_redundancy():
    metrics = {
        "semantic_coherence": 0.7,
        "structural_balance": 0.8,
        "topic_flow": 0.9,
        "redundancy": 0.6,  # превышает порог
        "final_score": 0.8
    }
    thresholds = resolve_thresholds()
    advice = generate_advice(metrics, thresholds, has_reference=True)
    assert any("повторяющиеся или очень схожие темы" in a for a in advice)


def test_advice_for_low_semantic_coherence():
    metrics = {
        "semantic_coherence": 0.4,
        "structural_balance": 0.8,
        "redundancy": 0.1,
        "final_score": 0.7
    }
    thresholds = resolve_thresholds()
    advice = generate_advice(metrics, thresholds, has_reference=False)
    assert any("Темы в разделах" in a for a in advice)


def test_advice_for_good_course():
    metrics = {
        "semantic_coherence": 0.75,
        "structural_balance": 0.85,
        "redundancy": 0.1,
        "final_score": 0.9
    }
    thresholds = resolve_thresholds()
    advice = generate_advice(metrics, thresholds, has_reference=False)
    assert advice == ["Курс хорошо структурирован — 👍 Темы логичны и сбалансированы!"]
