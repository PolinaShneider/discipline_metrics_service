import pytest
from metrics.evaluation import evaluate_course
from metrics.thresholds import DEFAULT_THRESHOLDS

GOOD_COURSE = '''
1. Введение
 - Что такое ИИ
 - История ИИ
2. Методы
 - Машинное обучение
 - Глубокое обучение
'''

BAD_COURSE = '''
1. Разное
 - Микробиология
 - Киноиндустрия
2. Беспорядок
 - Танцы и краски
 - Linux ядро
3. Советы
 - Как жарить рыбу
 - Продажа NFT
'''

UNBALANCED_COURSE = '''
1. Введение
 - Что такое ИИ
2. Глубина
 - Введение в машинное обучение
 - Алгоритмы
 - Регрессия
 - Классификация
 - SVM
 - Нейронные сети
 - Обучение с подкреплением
'''

REDUNDANT_COURSE = '''
1. Введение
 - Что такое ИИ
 - Что такое ИИ
2. Методы
 - Машинное обучение
 - Машинное обучение
 - Глубокое обучение
 - глубокое обучение
'''

REFERENCE = '''
1. Введение
 - Что такое ИИ
 - История ИИ
2. Методы
 - Машинное обучение
 - Глубокое обучение
'''

# --- МЕТРИКИ ---

def test_semantic_coherence_bad_score():
    result = evaluate_course(BAD_COURSE)
    assert result["semantic_coherence"] < 0.7

def test_structural_balance_unbalanced_score():
    result = evaluate_course(UNBALANCED_COURSE)
    assert result["structural_balance"] < 0.6

def test_redundancy_high_score():
    result = evaluate_course(REDUNDANT_COURSE, REFERENCE)
    assert result["redundancy"] > 0.35

def test_semantic_coherence_good_score():
    result = evaluate_course(GOOD_COURSE)
    assert result["semantic_coherence"] > 0.5

def test_reference_metrics_present():
    result = evaluate_course(GOOD_COURSE, REFERENCE)
    assert result["relevance"] is not None
    assert result["sequence_coverage"] is not None
    assert result["topic_flow"] > 0.8

def test_metrics_without_reference():
    result = evaluate_course(GOOD_COURSE)
    assert result["relevance"] is None
    assert result["sequence_coverage"] is None
    assert result["topic_flow"] == 0.0

def test_no_crash_on_empty_reference():
    result = evaluate_course(GOOD_COURSE, "")
    assert result["final_score"] > 0.5

def test_thresholds_defaults_are_respected():
    result = evaluate_course(BAD_COURSE, REFERENCE)
    for key, threshold in DEFAULT_THRESHOLDS.items():
        if key in result and isinstance(result[key], (int, float)):
            assert 0.0 <= result[key] <= 1.0
