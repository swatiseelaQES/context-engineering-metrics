from openai import OpenAI
import numpy as np
import os

import httpx

#verify_ssl = os.getenv("OPENAI_VERIFY_SSL", "true").lower() == "true"

http_client = httpx.Client(
    verify=False
)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    http_client=http_client,
)

EMBEDDING_MODEL = "text-embedding-3-small"


def get_embedding(text: str):
    if not text:
        return []

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )

    return response.data[0].embedding


def cosine_similarity(vec1, vec2):
    if not vec1 or not vec2:
        return 0.0

    v1 = np.array(vec1)
    v2 = np.array(vec2)

    denominator = np.linalg.norm(v1) * np.linalg.norm(v2)

    if denominator == 0:
        return 0.0

    return float(np.dot(v1, v2) / denominator)