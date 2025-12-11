# Escalation Helper

AI-powered SQL troubleshooting assistant for the HungerRush installer team. Describe a problem in plain English and get the SQL query you need.

## Quick Start

```bash
# 1. Setup environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure API key
cp .env.template .env
# Edit .env and add your OpenAI API key

# 3. Build knowledge base
python ingest.py

# 4. Run the app
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## How It Works

1. **Ask a question** - "Cashier can't void an order" or "Customer was charged twice"
2. **Get SQL queries** - Relevant queries from the knowledge base with explanations
3. **Follow-up questions** - If results are uncertain, the system asks clarifying questions

## Adding Knowledge

Add or update markdown files in `data/`, then rebuild:

```bash
python ingest.py
```

## Configuration

Edit `config.py` to adjust:
- Search thresholds and result counts
- OpenAI models (embedding and LLM)
- Chunk sizes for document processing

## Tech Stack

- **Streamlit** - Web interface
- **ChromaDB** - Vector database for semantic search
- **OpenAI** - Embeddings (ada-002) and LLM (gpt-4o-mini)
- **sentence-transformers** - Cross-encoder reranking for improved accuracy
