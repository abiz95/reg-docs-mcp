from mcp.server.fastmcp import FastMCP
from embeddings import embed_text
from opensearch_client import search_similar

mcp = FastMCP("reg-docs-mcp")


@mcp.tool()
def search_docs(query: str, top_k: int = 5) -> str:
    """Semantic search over ingested insurance/regulatory documents. Returns
    the most relevant passages with their source file, so answers can be
    grounded and cited rather than generated from memory."""
    query_embedding = embed_text(query)
    results = search_similar(query_embedding, top_k)

    if not results:
        return "No matching passages found. Has ingest.py been run yet?"

    return "\n\n---\n\n".join(
        f"[{i + 1}] (source: {r.source}, chunk {r.chunk_index}, score: {r.score:.3f})\n{r.text}"
        for i, r in enumerate(results)
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")