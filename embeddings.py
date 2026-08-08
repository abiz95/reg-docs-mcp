from functools import lru_cache
from sentence_transformers import SentenceTransformer
import config


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    """Loads the embedding model once and reuses it. Runs entirely locally
    on CPU - no API key, no per-call cost, no network dependency after the
    model has been downloaded and cached the first time."""
    return SentenceTransformer(config.EMBEDDING_MODEL)


def embed_text(text: str) -> list[float]:
    model = get_model()
    vector = model.encode(text, normalize_embeddings=True)
    return vector.tolist()


def embed_batch(texts: list[str]) -> list[list[float]]:
    model = get_model()
    vectors = model.encode(texts, normalize_embeddings=True, batch_size=16)
    return vectors.tolist()