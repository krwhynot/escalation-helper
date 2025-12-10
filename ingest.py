"""
================================================
Escalation Helper - Document Ingestion
================================================
Reads markdown documents, chunks them, and stores
embeddings in ChromaDB for semantic search.
================================================
"""

import os
import glob
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI

import config


def get_markdown_files(data_dir: str) -> list[str]:
    """Find all markdown files in the data directory recursively."""
    pattern = os.path.join(data_dir, "**", "*.md")
    files = glob.glob(pattern, recursive=True)
    return files


def read_file(file_path: str) -> str:
    """Read and return contents of a file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """
    Split text into overlapping chunks.

    Args:
        text: The text to split
        chunk_size: Maximum characters per chunk
        overlap: Number of overlapping characters between chunks

    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # Try to break at a natural point (newline or period)
        if end < len(text):
            # Look for a good break point in the last 200 chars of the chunk
            search_start = max(end - 200, start)
            last_newline = text.rfind("\n\n", search_start, end)
            last_period = text.rfind(". ", search_start, end)

            if last_newline > search_start:
                end = last_newline + 2
            elif last_period > search_start:
                end = last_period + 2

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap

    return chunks


def ingest_documents():
    """Main ingestion pipeline."""
    # Validate configuration
    issues = config.validate_config()
    if issues:
        print("Configuration errors:")
        for issue in issues:
            print(f"  - {issue}")
        return

    print(f"Starting document ingestion...")
    print(f"Data directory: {config.DATA_DIR}")

    # Find all markdown files
    files = get_markdown_files(config.DATA_DIR)
    if not files:
        print("No markdown files found in data directory.")
        print("Add .md files to the data/ folder and run again.")
        return

    print(f"Found {len(files)} markdown file(s)")

    # Initialize ChromaDB
    client = chromadb.PersistentClient(path=config.CHROMA_DB_PATH)

    # Create OpenAI embedding function
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=config.OPENAI_API_KEY,
        model_name=config.EMBEDDING_MODEL
    )

    # Delete existing collection if it exists (fresh start)
    try:
        client.delete_collection(name=config.COLLECTION_NAME)
        print(f"Deleted existing collection: {config.COLLECTION_NAME}")
    except Exception:
        pass  # Collection doesn't exist

    # Create new collection with cosine distance metric
    # Note: OpenAI ada-002 embeddings are normalized, so cosine gives 0-1 interpretable scores
    collection = client.create_collection(
        name=config.COLLECTION_NAME,
        embedding_function=openai_ef,
        metadata={
            "hnsw:space": "cosine",  # Use cosine similarity (0=identical, 1=unrelated)
            "description": "Escalation Helper knowledge base"
        }
    )

    # Process each file
    all_chunks = []
    all_metadatas = []
    all_ids = []

    for file_path in files:
        print(f"Processing: {file_path}")
        content = read_file(file_path)

        # Chunk the document
        chunks = chunk_text(
            content,
            config.CHUNK_SIZE,
            config.CHUNK_OVERLAP
        )

        # Create metadata and IDs for each chunk
        file_name = Path(file_path).name
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_metadatas.append({
                "source": file_name,
                "file_path": file_path,
                "chunk_index": i
            })
            all_ids.append(f"{file_name}_{i}")

        print(f"  -> {len(chunks)} chunks")

    # Add all documents to collection
    if all_chunks:
        print(f"\nCreating embeddings for {len(all_chunks)} chunks...")
        collection.add(
            documents=all_chunks,
            metadatas=all_metadatas,
            ids=all_ids
        )
        print("Embeddings created and stored successfully!")

    print(f"\nIngestion complete!")
    print(f"Total chunks: {len(all_chunks)}")
    print(f"Database location: {config.CHROMA_DB_PATH}")


if __name__ == "__main__":
    ingest_documents()
