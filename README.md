# reg-docs-mcp

An MCP (Model Context Protocol) server that answers questions over
insurance and regulatory documents using retrieval-augmented generation
(RAG). Any MCP-compatible AI client (Claude Desktop, Claude Code, Cursor)
can call it as a tool to get grounded, cited answers instead of relying on
the model's memory.

Everything in this stack is free and runs locally — no AWS account, no API
keys, no per-call cost.

| Component | Technology |
|---|---|
| Embeddings | `sentence-transformers` (`all-MiniLM-L6-v2`), running locally on CPU |
| Vector store | Open-source OpenSearch, self-hosted via Docker |
| Tool protocol | Official Python MCP SDK (`mcp`) |

## How it works

1. Regulatory documents (plain text) are chunked into overlapping passages.
2. Each chunk is embedded locally with a small sentence-transformer model.
3. Chunks and their embeddings are indexed into OpenSearch as `knn_vector` fields.
4. The MCP server exposes a `search_docs` tool: given a natural-language
   query, it embeds the query the same way, runs a k-NN similarity search,
   and returns the top matching passages with their source file and score.
5. An AI client calling the tool gets real, citable text back — not a
   hallucinated summary.

## Prerequisites

- Python 3.10+
- Docker (for local OpenSearch)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

docker compose up -d           # starts OpenSearch + OpenSearch Dashboards
python3 ingest.py              # chunks, embeds, and indexes the sample docs
python3 mcp_server.py          # runs the MCP server on stdio
```

The first `ingest.py` run downloads the embedding model from Hugging Face
(~90 MB) and caches it locally — after that, everything runs offline.

## Using it from an AI client

Add this to your MCP client config (e.g. Claude Desktop's
`claude_desktop_config.json`), using **absolute paths**:

```json
{
  "mcpServers": {
    "reg-docs": {
      "command": "/absolute/path/to/reg-docs-mcp/.venv/bin/python",
      "args": ["/absolute/path/to/reg-docs-mcp/mcp_server.py"]
    }
  }
}
```

Then ask the client something like "What's the difference between the SCR
and the MCR under Solvency II?" and it will call `search_docs` and answer
from the retrieved passages.

## Inspecting the index

OpenSearch Dashboards is available at **http://localhost:5601** once the
containers are up. Under **Dev Tools**, you can query the index directly
to confirm ingestion worked:

```
GET reg-docs/_search
{
  "query": { "match_all": {} },
  "size": 3
}
```

## Adding real documents

`data/sample_docs/` ships with a few short, original placeholder summaries
(written for this project, not copied from any official source) so the
pipeline works out of the box. For a fuller, more realistic demo, add
plain-text extracts from public regulatory sources, for example:

- FCA Handbook — https://www.handbook.fca.org.uk
- Bank of England / PRA Rulebook — https://www.prarulebook.co.uk
- EIOPA (Solvency II) — https://www.eiopa.europa.eu
- IFRS Foundation — https://www.ifrs.org

Drop `.txt` files into `data/sample_docs/` and re-run `python3 ingest.py`.

## Project structure

```
reg-docs-mcp/
├── requirements.txt
├── docker-compose.yml       OpenSearch + OpenSearch Dashboards, local only
├── .env.example
├── config.py                 environment/config loading
├── chunk.py                  paragraph/sentence-aware text chunking
├── embeddings.py              local embedding model wrapper
├── opensearch_client.py        index creation, bulk indexing, k-NN search
├── ingest.py                    ingestion pipeline entry point
├── mcp_server.py                 MCP server exposing the search_docs tool
└── data/
    └── sample_docs/               sample text documents
```

All modules sit flat in the project root rather than inside a package —
MCP clients launch `mcp_server.py` directly as a script, and package-
relative imports don't resolve in that context.

## Notes

- The OpenSearch containers disable the security plugin for local
  development convenience. Do not use this configuration for anything
  exposed beyond localhost.
- `all-MiniLM-L6-v2` produces 384-dimensional embeddings; if you swap in a
  different embedding model, update `EMBEDDING_DIMS` in `config.py` to
  match.

## License

MIT
