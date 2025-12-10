# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Escalation Helper is an AI-powered SQL troubleshooting assistant for the HungerRush installer team. Users describe a problem in natural language (e.g., "cashier can't void an order") and the system returns relevant SQL queries with explanations.

**Tech Stack:** Python, Streamlit (web UI), ChromaDB (vector database), OpenAI API (embeddings + LLM)

## Build Commands

```bash
# Setup (first time)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Build knowledge base (after adding/updating documents)
python ingest.py

# Run the app
streamlit run app.py

# Alternative port if 8501 is in use
streamlit run app.py --server.port 8502

# Validate configuration
python config.py
```

## Architecture

### Data Flow
1. `ingest.py` reads markdown files from `data/` directory
2. Documents are chunked (2000 chars, 200 overlap) and embedded via OpenAI
3. Embeddings stored in ChromaDB (`chroma_db/` directory)
4. `app.py` provides Streamlit UI for semantic search
5. User queries return top 3 relevant chunks + LLM-generated response

### Key Configuration (config.py)
- `EMBEDDING_MODEL`: text-embedding-ada-002
- `LLM_MODEL`: gpt-4o-mini
- `CHUNK_SIZE`: 2000 chars
- `TOP_K_RESULTS`: 3
- `COLLECTION_NAME`: escalation_docs

### Data Sources
- `data/sql_reference.md`: Primary source - SQL troubleshooting queries
- `data/confluence/`: Future expansion for Confluence docs

## Environment Variables

Copy `.env.template` to `.env` and set:
- `OPENAI_API_KEY`: Required for embeddings and LLM
- `APP_PASSWORD`: Simple team access password (default: escalation2024)
