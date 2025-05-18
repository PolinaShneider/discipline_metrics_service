import numpy as np
from itertools import combinations
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx

bert_model = SentenceTransformer('all-MiniLM-L6-v2')


def topic_flow_score(course_structure, reference_order):
    all_topics = [topic for topics in course_structure.values() for topic in topics]
    filtered_course = [x for x in all_topics if x in reference_order]

    if not filtered_course:
        return 0.0

    ref_positions = {t: i for i, t in enumerate(reference_order)}
    seq_indices = [ref_positions[t] for t in filtered_course if t in ref_positions]

    if not seq_indices:
        return 0.0

    def kendall_tau_distance(seq1, seq2):
        inv_count = 0
        for i in range(len(seq1)):
            for j in range(i + 1, len(seq1)):
                if seq1[i] > seq1[j]:
                    inv_count += 1
        return inv_count

    dist = kendall_tau_distance(seq_indices, list(range(len(seq_indices))))
    penalty = all_topics.index(filtered_course[0]) / len(all_topics) if filtered_course else 1
    max_inv = len(seq_indices) * (len(seq_indices) - 1) / 2 if len(seq_indices) > 1 else 1

    return max(0, (1 - dist / max_inv) * (1 - penalty))


def sequence_based_coverage(course_structure, reference_topics, threshold=0.8):
    all_topics = set(topic for topics in course_structure.values() for topic in topics)
    if not all_topics or not reference_topics:
        return 0.0

    course_embeddings = bert_model.encode(list(all_topics))
    reference_embeddings = bert_model.encode(reference_topics)

    similarity_matrix = cosine_similarity(course_embeddings, reference_embeddings)
    matched_topics = np.sum(np.max(similarity_matrix, axis=1) > threshold)

    return min(1.0, matched_topics / len(reference_topics))


def build_topic_graph(course_structure):
    G = nx.Graph()
    for topics in course_structure.values():
        for topic in topics:
            G.add_node(topic)
        for i in range(len(topics) - 1):
            G.add_edge(topics[i], topics[i + 1])
    return G


def semantic_node_mapping(course_nodes, ref_nodes, threshold=0.8):
    if not course_nodes or not ref_nodes:
        return {}

    course_emb = bert_model.encode(list(course_nodes))
    ref_emb = bert_model.encode(list(ref_nodes))

    mapping = {}
    for i, c_node in enumerate(course_nodes):
        best_sim, best_ref = 0.0, None
        for j, r_node in enumerate(ref_nodes):
            sim = cosine_similarity([course_emb[i]], [ref_emb[j]])[0, 0]
            if sim > best_sim:
                best_sim, best_ref = sim, r_node
        if best_sim > threshold:
            mapping[c_node] = best_ref
    return mapping


def graph_based_coverage(course_structure, reference_structure, threshold=0.75):
    course_graph = build_topic_graph(course_structure)
    reference_graph = build_topic_graph(reference_structure)

    node_map = semantic_node_mapping(course_graph.nodes(), reference_graph.nodes(), threshold)
    matched_nodes = len(node_map)

    renamed_edges = {
        (node_map[a], node_map[b]) for a, b in course_graph.edges()
        if a in node_map and b in node_map
    }

    ref_edges = set(reference_graph.edges())
    matched_edges = len(renamed_edges & ref_edges)

    total_nodes = len(reference_graph.nodes())
    total_edges = len(reference_graph.edges())

    if total_nodes + total_edges == 0:
        return 0.0

    return min(1.0, (matched_nodes + matched_edges) / (total_nodes + total_edges))


def redundancy_score(course_structure):
    all_topics = [topic for topics in course_structure.values() for topic in topics]
    if len(all_topics) < 2:
        return 0.0

    embeddings = bert_model.encode(all_topics)
    sim_matrix = cosine_similarity(embeddings)

    redundancy_scores = []
    lex_duplicates = 0

    for i, j in combinations(range(len(all_topics)), 2):
        sim = sim_matrix[i, j]
        if all_topics[i].lower() == all_topics[j].lower():
            lex_duplicates += 1
            redundancy_scores.append(0.9)
        elif sim > 0.8:
            penalty = (sim - 0.8) ** 2
            if sim > 0.95:
                penalty += (sim - 0.8) ** 3
            redundancy_scores.append(penalty)

    base_score = np.mean(redundancy_scores) if redundancy_scores else 0.0
    correction_factor = min(1.0, (len(redundancy_scores) / len(all_topics)) ** 0.8 + lex_duplicates * 0.05)

    return min(1.0, base_score * correction_factor)


def relevance_score(course_structure, reference_topics, threshold=0.7):
    all_topics = set(topic for topics in course_structure.values() for topic in topics)
    if not all_topics or not reference_topics:
        return 0.0

    course_embeddings = bert_model.encode(list(all_topics))
    reference_embeddings = bert_model.encode(reference_topics)

    similarity_matrix = cosine_similarity(course_embeddings, reference_embeddings)
    relevant_topics = np.sum(np.max(similarity_matrix, axis=1) > threshold)

    return min(1.0, relevant_topics / len(all_topics))


def extra_topics_penalty(course_structure, reference_topics, threshold=0.85):
    all_topics = set(topic for topics in course_structure.values() for topic in topics)
    if not all_topics:
        return 0.0

    course_embeddings = bert_model.encode(list(all_topics))
    reference_embeddings = bert_model.encode(reference_topics)

    similarity_matrix = cosine_similarity(course_embeddings, reference_embeddings)
    extra_topics = np.sum(np.max(similarity_matrix, axis=1) < threshold)

    return min(1.0, extra_topics / len(all_topics))
