"""
================================================
Escalation Helper - Configuration
================================================
All settings in one place for easy management.
================================================
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ================================================
# API Configuration
# ================================================

# OpenAI API key (loaded from .env)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Models to use
EMBEDDING_MODEL = "text-embedding-ada-002"  # $0.0001 per 1K tokens
LLM_MODEL = "gpt-4o-mini"                    # $0.00015 per 1K input tokens

# ================================================
# ChromaDB Configuration
# ================================================

# Where to store the vector database
CHROMA_DB_PATH = "./chroma_db"

# Collection name for our documents
COLLECTION_NAME = "escalation_docs"

# ================================================
# Document Processing
# ================================================

# How many characters per chunk (roughly 500 words)
CHUNK_SIZE = 2000

# Overlap between chunks to maintain context
CHUNK_OVERLAP = 200

# How many results to return from search
TOP_K_RESULTS = 3

# ================================================
# Search Optimization
# ================================================

# Distance threshold for cosine similarity (0.0 = identical, 1.0 = unrelated)
# Results with distance > threshold will be filtered out
DISTANCE_THRESHOLD = 0.40  # 60% similarity minimum

# How many candidates to retrieve for reranking (get more than needed)
RETRIEVE_K = 20

# Final number of results to show user
RETURN_K = 3

# Cross-encoder model for reranking (downloads ~90MB on first use)
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# ================================================
# Authentication
# ================================================

# Simple password for team access
APP_PASSWORD = os.getenv("APP_PASSWORD", "escalation2024")

# ================================================
# Paths
# ================================================

# Where source documents are stored
DATA_DIR = "./data"
SQL_REFERENCE_FILE = "./data/sql_reference.md"
CONFLUENCE_DIR = "./data/confluence"

# ================================================
# Streamlit UI Configuration
# ================================================

PAGE_TITLE = "Escalation Helper"
PAGE_ICON = "🔍"

# ================================================
# Validation
# ================================================

def validate_config():
    """
    Check that all required configuration is present.
    Returns a list of any missing items.
    """
    issues = []
    
    if not OPENAI_API_KEY or OPENAI_API_KEY == "sk-your-api-key-here":
        issues.append("OPENAI_API_KEY not set in .env file")
    
    if not os.path.exists(DATA_DIR):
        issues.append(f"Data directory not found: {DATA_DIR}")
    
    return issues


# Run validation when module is imported
if __name__ == "__main__":
    issues = validate_config()
    if issues:
        print("⚠️  Configuration Issues Found:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("✅ Configuration looks good!")
