import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

bert_model = SentenceTransformer('all-MiniLM-L6-v2')

def revised_semantic_coherence(course_structure):
    scores = []
    for section, topics in course_structure.items():
        if len(topics) < 2:
            continue
        embeddings = bert_model.encode(topics)
        sim_matrix = np.inner(embeddings, embeddings)
        mean_sim = np.mean(sim_matrix)
        std_sim = np.std(sim_matrix)

        coherence_score = mean_sim * (1 - min(std_sim, 0.5))
        scores.append(coherence_score)

    return max(0, np.mean(scores)) if scores else 0

def structural_balance(course_structure):
    topic_counts = np.array([len(topics) for topics in course_structure.values()])
    if len(topic_counts) < 2:
        return 1.0
    std_dev = np.std(topic_counts)
    mean_topics = np.mean(topic_counts)
    max_jump = np.max(np.abs(np.diff(topic_counts)))
    balance_score = 1 - ((std_dev / mean_topics) + (max_jump / max(topic_counts))) / 2
    balance_score -= 0.1 * (max_jump > mean_topics * 0.5)
    return max(0, balance_score)
