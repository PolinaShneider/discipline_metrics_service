from metrics.parsing import parse_course_structure
from metrics.thresholds import resolve_thresholds
from metrics.metrics_independent import revised_semantic_coherence, structural_balance
from metrics.metrics_reference import (
    topic_flow_score,
    sequence_based_coverage,
    graph_based_coverage,
    redundancy_score,
    relevance_score,
    extra_topics_penalty
)


def compute_structural_scores(course_text, reference_text=None):
    course_structure = parse_course_structure(course_text)
    semantic_score = revised_semantic_coherence(course_structure)
    balance = structural_balance(course_structure)

    if reference_text:
        reference_structure = parse_course_structure(reference_text)
        reference_topics = [topic for topics in reference_structure.values() for topic in topics]
        topic_flow = topic_flow_score(course_structure, reference_topics)
    else:
        topic_flow = 0.0

    return semantic_score, topic_flow, balance


def compute_coverage_scores(course_text, reference_text):
    course_structure = parse_course_structure(course_text)
    reference_structure = parse_course_structure(reference_text)
    reference_topics = [topic for topics in reference_structure.values() for topic in topics]

    seq_cov = sequence_based_coverage(course_structure, reference_topics)
    graph_cov = graph_based_coverage(course_structure, reference_structure)
    redundancy = redundancy_score(course_structure)

    return (seq_cov, graph_cov), redundancy


def compute_relevance_scores(course_text, reference_text):
    course_structure = parse_course_structure(course_text)
    reference_topics = [topic for topics in parse_course_structure(reference_text).values() for topic in topics]

    relevance = relevance_score(course_structure, reference_topics)
    extra_topics = extra_topics_penalty(course_structure, reference_topics)

    return relevance, extra_topics


def compute_final_score(structural, coverage=None, relevance=None, redundancy=0.0, extra_topics=0.0):
    semantic_norm = min(structural[0] / 0.65, 1.0)
    topic_flow = structural[1]
    balance_norm = min(structural[2] / 0.8, 1.0)

    structural_score = (semantic_norm + topic_flow + balance_norm) / 3

    if coverage and relevance is not None:
        seq_cov, graph_cov = coverage
        redundancy_penalty = min(redundancy, 1.0)
        relevance_norm = relevance
        extra_penalty = min(extra_topics, 0.5)

        coverage_score = (seq_cov + graph_cov - redundancy_penalty) / 2
        relevance_score_val = max(0, relevance_norm - extra_penalty)

        final_score = min(1.0, (structural_score + coverage_score + relevance_score_val) / 3)
    else:
        coverage_score = None
        relevance_score_val = None
        final_score = round(structural_score, 3)

    return {
        "final_score": final_score,
        "structural_score": structural_score,
        "semantic_coherence": structural[0],
        "topic_flow": structural[1],
        "structural_balance": structural[2],
        "sequence_coverage": coverage[0] if coverage else None,
        "graph_coverage": coverage[1] if coverage else None,
        "redundancy": redundancy,
        "relevance": relevance,
        "extra_topics_penalty": extra_topics,
        "coverage_score": coverage_score,
        "relevance_score": relevance_score_val,
    }

def generate_advice(result: dict, thresholds: dict, has_reference: bool = True) -> list[str]:
    a = []

    if result.get("semantic_coherence", 1) < thresholds["semantic_coherence"]:
        a.append("Темы в разделах слабо связаны — стоит пересмотреть формулировки или сгруппировать иначе.")

    if result.get("structural_balance", 1) < thresholds["structural_balance"]:
        a.append("Темы распределены неравномерно — попробуйте сбалансировать количество тем в разделах.")

    if has_reference:
        if result.get("topic_flow", 1) < thresholds["topic_flow"]:
            a.append("Порядок тем отличается от эталона — стоит пересмотреть структуру.")
        if result.get("sequence_coverage") is None:
            a.append("Добавьте эталон, чтобы рассчитать покрытие.")
        elif result.get("sequence_coverage", 1) < thresholds["sequence_coverage"]:
            a.append("Покрытие тем недостаточное — часть ключевых тем из эталона отсутствует.")

    if result.get("redundancy", 0) > thresholds["redundancy"]:
        a.append("Обнаружены повторяющиеся или очень схожие темы — стоит их объединить или удалить.")

    if result.get("final_score", 1) < thresholds["final_score"]:
        a.append("Итоговый балл ниже рекомендуемого — обратите внимание на слабые метрики.")

    if not a:
        a.append("Курс хорошо структурирован — 👍 Темы логичны и сбалансированы!")

    return a


def evaluate_course(course_text: str, reference_text: str = None, thresholds: dict = None) -> dict:
    thresholds = resolve_thresholds(thresholds)

    def get(name, default):
        return thresholds.get(name, default)

    structural = compute_structural_scores(course_text, reference_text)

    if reference_text and reference_text.strip():
        coverage, redundancy = compute_coverage_scores(course_text, reference_text)
        relevance, extra_topics = compute_relevance_scores(course_text, reference_text)
        result = compute_final_score(structural, coverage, relevance, redundancy, extra_topics)
    else:
        result = compute_final_score(structural)

    has_reference = bool(reference_text and reference_text.strip())
    result["advice"] = generate_advice(result, thresholds, has_reference=has_reference)

    return result

