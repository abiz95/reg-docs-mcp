import os
from dotenv import load_dotenv

load_dotenv()

OPENSEARCH_URL = os.getenv("OPENSEARCH_URL", "http://localhost:9200")
INDEX_NAME = os.getenv("OPENSEARCH_INDEX", "reg-docs")
DOCS_DIR = os.getenv("DOCS_DIR", "data/sample_docs")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "120"))
# all-MiniLM-L6-v2 outputs 384-dimensional embeddings.
EMBEDDING_DIMS = 384