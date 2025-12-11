# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Escalation Helper is an AI-powered SQL troubleshooting assistant for the HungerRush installer team. Users describe a problem in natural language (e.g., "cashier can't void an order") and the system returns relevant SQL queries with explanations.

**Tech Stack:** Python 3.12, Streamlit, ChromaDB, OpenAI API (embeddings + LLM), sentence-transformers (cross-encoder reranking)

## Build Commands

```bash
# Setup (first time)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Build knowledge base (after adding/updating documents in data/)
python ingest.py

# Run the app
streamlit run app.py

# Alternative port if 8501 is in use
streamlit run app.py --server.port 8502

# Validate configuration
python config.py
```

## Architecture

### Core Files
- `app.py` - Streamlit web UI with chat interface, authentication, and follow-up question flow
- `ingest.py` - Document ingestion pipeline: reads markdown, chunks text, creates embeddings
- `config.py` - All configuration constants (models, thresholds, paths)

### Search Pipeline (Two-Stage RAG)
1. **Ingestion** (`ingest.py`): Markdown files in `data/` are chunked (2000 chars, 200 overlap), embedded via OpenAI ada-002, stored in ChromaDB with cosine similarity
2. **Retrieval** (`app.py:search_knowledge_base`): Query retrieves 20 candidates from ChromaDB
3. **Reranking**: Optional cross-encoder (`ms-marco-MiniLM-L-6-v2`) reorders by relevance
4. **Response**: Top 3 results passed to GPT-4o-mini for natural language response

### Follow-up Question System
When search confidence is low (distance > 0.30), the app asks clarifying questions based on detected category (printer, payment, employee, order, menu, cash). Configuration is in `FOLLOWUP_QUESTIONS` dict in `app.py`.

### Key Thresholds (config.py)
- `DISTANCE_THRESHOLD`: 0.40 (60% similarity minimum)
- `RETRIEVE_K`: 20 (candidates for reranking)
- `RETURN_K`: 3 (final results shown)

### Data Sources
- `data/sql_reference.md` - Primary SQL troubleshooting queries
- `data/*.md` - Additional reference docs (ERD, column mappings, permissions)
- `data/confluence/` - Confluence exports

## Environment Variables

Copy `.env.template` to `.env` and set:
- `OPENAI_API_KEY`: Required for embeddings and LLM
- `APP_PASSWORD`: Team access password (default: escalation2024)
