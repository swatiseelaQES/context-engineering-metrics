from shared.llm.embeddings import (
    get_embedding,
    cosine_similarity,
)


def task_completion_score(output, expected_root_cause):
    """
    Semantic similarity between:
    - agent diagnosis
    - expected diagnosis
    """

    if not output or not expected_root_cause:
        return 0.0

    output_embedding = get_embedding(output)
    expected_embedding = get_embedding(expected_root_cause)

    similarity = cosine_similarity(
        output_embedding,
        expected_embedding,
    )

    return round(similarity, 4)