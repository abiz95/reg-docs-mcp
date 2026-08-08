from dataclasses import dataclass
from opensearchpy import OpenSearch
import config

client = OpenSearch(hosts=[config.OPENSEARCH_URL])


def ensure_index() -> None:
    """Creates the index with a k-NN vector field if it doesn't already
    exist. Safe to call on every ingest run."""
    if client.indices.exists(index=config.INDEX_NAME):
        return

    client.indices.create(
        index=config.INDEX_NAME,
        body={
            "settings": {"index": {"knn": True}},
            "mappings": {
                "properties": {
                    "text": {"type": "text"},
                    "source": {"type": "keyword"},
                    "chunk_index": {"type": "integer"},
                    "embedding": {
                        "type": "knn_vector",
                        "dimension": config.EMBEDDING_DIMS,
                        "method": {
                            "name": "hnsw",
                            "space_type": "cosinesimil",
                            "engine": "lucene",
                        },
                    },
                }
            },
        },
    )


def index_chunks(chunks: list[dict]) -> None:
    if not chunks:
        return

    bulk_body = []
    for chunk in chunks:
        bulk_body.append({"index": {"_index": config.INDEX_NAME}})
        bulk_body.append(chunk)

    response = client.bulk(body=bulk_body)
    if response.get("errors"):
        failed = [item for item in response["items"] if item.get("index", {}).get("error")]
        raise RuntimeError(f"{len(failed)} chunk(s) failed to index: {failed[:3]}")


@dataclass
class SearchResult:
    text: str
    source: str
    chunk_index: int
    score: float


def search_similar(query_embedding: list[float], top_k: int = 5) -> list[SearchResult]:
    response = client.search(
        index=config.INDEX_NAME,
        body={
            "size": top_k,
            "query": {"knn": {"embedding": {"vector": query_embedding, "k": top_k}}},
        },
    )

    return [
        SearchResult(
            text=hit["_source"]["text"],
            source=hit["_source"]["source"],
            chunk_index=hit["_source"]["chunk_index"],
            score=hit["_score"],
        )
        for hit in response["hits"]["hits"]
    ]