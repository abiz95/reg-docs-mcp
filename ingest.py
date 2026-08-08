from pathlib import Path
import config
from chunk import chunk_text
from embeddings import embed_batch
from opensearch_client import ensure_index, index_chunks


def main() -> None:
    docs_dir = Path(config.DOCS_DIR)
    print(f"Reading documents from {docs_dir}")
    files = sorted(docs_dir.glob("*.txt"))

    if not files:
        print(f"No .txt files found in {docs_dir}.")
        return

    print("Ensuring OpenSearch index exists...")
    ensure_index()

    total_chunks = 0
    for file_path in files:
        raw = file_path.read_text(encoding="utf-8")
        chunks = chunk_text(raw, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
        print(f"  {file_path.name}: {len(chunks)} chunk(s)")

        embeddings = embed_batch([c.text for c in chunks])

        to_index = [
            {
                "text": chunk.text,
                "source": file_path.name,
                "chunk_index": chunk.index,
                "embedding": embedding,
            }
            for chunk, embedding in zip(chunks, embeddings)
        ]
        index_chunks(to_index)
        total_chunks += len(chunks)

    print(f"Done. Indexed {total_chunks} chunk(s) from {len(files)} file(s).")


if __name__ == "__main__":
    main()