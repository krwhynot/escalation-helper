# Cross-Encoder Reranking

This is the single most impactful improvement you can make to search accuracy. It typically improves relevance by 20-40% over bi-encoder search alone.

## The Problem with Bi-Encoders

ChromaDB uses a bi-encoder approach (via OpenAI embeddings):

```
Query: "cashier can't void order"  →  [vector1]
Doc:   "How to void transactions"  →  [vector2]

Similarity = compare vector1 vs vector2
```

The problem? Each text is encoded **independently**. The model doesn't see them together, so it can miss nuanced relationships.

## How Cross-Encoders Work

A cross-encoder sees the query AND document together:

```
Input: ["cashier can't void order", "How to void transactions"]
       ↓
   Transformer processes BOTH together
       ↓
Output: 0.87 relevance score
```

This attention across both texts catches relationships that bi-encoders miss.

## Two-Stage Retrieval Pipeline

The solution: use both approaches together.

```
User Query
    ↓
Stage 1: Bi-Encoder (ChromaDB)
    → Fast! Retrieve 20 candidates from thousands
    ↓
Stage 2: Cross-Encoder
    → Accurate! Rerank 20 candidates
    ↓
Return top 3 results
```

## Model Selection

MS MARCO cross-encoders are trained on real search queries - perfect for our use case.

| Model | Speed (docs/sec) | Quality (MRR@10) | Best For |
|-------|------------------|------------------|----------|
| `ms-marco-TinyBERT-L2-v2` | 9000 | 32.56 | Speed-critical apps |
| `ms-marco-MiniLM-L2-v2` | 4100 | 34.85 | Fast |
| `ms-marco-MiniLM-L4-v2` | 2500 | 37.70 | Balanced |
| **`ms-marco-MiniLM-L6-v2`** | **1800** | **39.01** | **Recommended** |
| `ms-marco-MiniLM-L12-v2` | 960 | 39.02 | Quality-focused |

**Recommendation**: `cross-encoder/ms-marco-MiniLM-L-6-v2` - best balance of speed and accuracy.

## Installation

```bash
pip install sentence-transformers
```

Add to `requirements.txt`:
```
sentence-transformers>=2.2.0
```

## Full Implementation

### Basic Reranking Function

```python
from sentence_transformers import CrossEncoder

# Initialize once at app startup (downloads ~90MB model first time)
cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')


def retrieve_and_rerank(
    query: str,
    collection,
    retrieve_k: int = 20,
    rerank_top_n: int = 3,
    distance_threshold: float = 0.40
) -> list:
    """
    Two-stage retrieval: ChromaDB retrieval + Cross-Encoder reranking.

    Args:
        query: User's search query
        collection: ChromaDB collection
        retrieve_k: Candidates to retrieve in stage 1
        rerank_top_n: Final results after reranking
        distance_threshold: Filter before reranking (optional)

    Returns:
        List of top reranked results with scores
    """
    # Stage 1: Retrieve candidates from ChromaDB
    results = collection.query(
        query_texts=[query],
        n_results=retrieve_k,
        include=["documents", "metadatas", "distances"]
    )

    if not results['documents'] or not results['documents'][0]:
        return []

    documents = results['documents'][0]
    metadatas = results['metadatas'][0]
    distances = results['distances'][0]

    # Optional: Pre-filter by distance threshold
    candidates = []
    for i, doc in enumerate(documents):
        if distances[i] <= distance_threshold:
            candidates.append({
                'document': doc,
                'metadata': metadatas[i],
                'chromadb_distance': distances[i]
            })

    if not candidates:
        return []

    # Stage 2: Rerank with Cross-Encoder
    pairs = [[query, c['document']] for c in candidates]
    scores = cross_encoder.predict(pairs)

    # Add scores and sort
    for i, candidate in enumerate(candidates):
        candidate['cross_encoder_score'] = float(scores[i])

    reranked = sorted(
        candidates,
        key=lambda x: x['cross_encoder_score'],
        reverse=True
    )

    return reranked[:rerank_top_n]
```

### Integration with Streamlit App

```python
# app.py

from sentence_transformers import CrossEncoder
import streamlit as st

# Cache the model so it loads once
@st.cache_resource
def load_cross_encoder():
    """Load cross-encoder model (cached)."""
    return CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')


def search_with_reranking(query: str, collection) -> dict:
    """
    Complete search function with reranking.

    Returns:
        Dict with 'success', 'results', and optional 'message'
    """
    cross_encoder = load_cross_encoder()

    # Stage 1: ChromaDB retrieval
    results = collection.query(
        query_texts=[query],
        n_results=20,  # Get more candidates for reranking
        include=["documents", "metadatas", "distances"]
    )

    if not results['documents'] or not results['documents'][0]:
        return {
            'success': False,
            'message': "No documents found in the knowledge base.",
            'results': []
        }

    # Filter by distance threshold
    candidates = []
    for i, doc in enumerate(results['documents'][0]):
        distance = results['distances'][0][i]
        if distance <= 0.50:  # Slightly higher threshold before reranking
            candidates.append({
                'document': doc,
                'metadata': results['metadatas'][0][i],
                'chromadb_distance': distance
            })

    if not candidates:
        return {
            'success': False,
            'message': f"No relevant results found for: '{query}'",
            'results': []
        }

    # Stage 2: Cross-encoder reranking
    pairs = [[query, c['document']] for c in candidates]
    scores = cross_encoder.predict(pairs)

    for i, candidate in enumerate(candidates):
        candidate['relevance_score'] = float(scores[i])

    # Sort by cross-encoder score
    reranked = sorted(candidates, key=lambda x: x['relevance_score'], reverse=True)

    # Take top 3
    top_results = []
    for result in reranked[:3]:
        top_results.append({
            'content': result['document'],
            'source': result['metadata'].get('source', 'Unknown'),
            'relevance_score': result['relevance_score'],
            'vector_distance': result['chromadb_distance'],
            'similarity_pct': round((1 - result['chromadb_distance']) * 100, 1)
        })

    return {
        'success': True,
        'results': top_results
    }
```

### Display Reranked Results

```python
def display_results(search_response):
    """Display search results in Streamlit."""
    if not search_response['success']:
        st.warning(search_response['message'])
        return

    for i, result in enumerate(search_response['results'], 1):
        with st.expander(
            f"Result {i}: {result['source']} "
            f"(Relevance: {result['relevance_score']:.2f})",
            expanded=(i == 1)
        ):
            st.markdown(result['content'])

            # Show both scores for transparency
            col1, col2 = st.columns(2)
            with col1:
                st.caption(f"Cross-Encoder Score: {result['relevance_score']:.3f}")
            with col2:
                st.caption(f"Vector Similarity: {result['similarity_pct']}%")
```

## Understanding Cross-Encoder Scores

Cross-encoder scores are NOT on a fixed scale like distances. They're relative relevance scores:

| Score Range | Meaning |
|-------------|---------|
| > 5.0 | Highly relevant |
| 2.0 - 5.0 | Relevant |
| 0.0 - 2.0 | Somewhat relevant |
| < 0.0 | Likely not relevant |

**Important**: Always use cross-encoder scores for **ranking**, not absolute thresholds. The same query might have all results between 1.0-3.0 or all between -2.0 to 0.5.

## Performance Optimization

### 1. Batch Processing

If you have multiple queries, batch them:

```python
def batch_rerank(queries: list, documents: list) -> list:
    """Rerank multiple queries at once."""
    all_pairs = []
    for query in queries:
        for doc in documents:
            all_pairs.append([query, doc])

    # Single batch prediction (much faster)
    all_scores = cross_encoder.predict(all_pairs)

    # Reshape back to per-query results
    # ... (implementation depends on your needs)
```

### 2. Reduce Candidate Count

If latency is critical, reduce `retrieve_k`:

```python
# Faster but might miss some relevant results
results = retrieve_and_rerank(query, collection, retrieve_k=10)

# Slower but better recall
results = retrieve_and_rerank(query, collection, retrieve_k=30)
```

### 3. Use Faster Model

For very latency-sensitive applications:

```python
# Faster model, slightly lower quality
cross_encoder = CrossEncoder('cross-encoder/ms-marco-TinyBERT-L-2-v2')
```

### 4. GPU Acceleration

If you have a GPU:

```python
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', device=device)
```

## Latency Expectations

For `ms-marco-MiniLM-L-6-v2` with 20 candidates:

| Hardware | Latency |
|----------|---------|
| CPU (modern laptop) | 100-300ms |
| CPU (older/server) | 200-500ms |
| GPU (any modern) | 20-50ms |

This is added to your ChromaDB query time (~50-100ms).

## When to Skip Reranking

Consider skipping reranking if:

1. **Single-word queries**: "void" - not much context for cross-encoder to work with
2. **Very high vector similarity**: If ChromaDB returns results with distance < 0.1, they're probably correct
3. **Latency-critical paths**: Consider async reranking or caching

```python
def smart_search(query: str, collection) -> list:
    """Skip reranking for simple queries or high-confidence results."""

    # Stage 1: ChromaDB
    results = collection.query(query_texts=[query], n_results=10)

    best_distance = results['distances'][0][0] if results['distances'][0] else 1.0

    # Skip reranking if top result is very confident
    if best_distance < 0.15:
        return format_results(results)

    # Skip for very short queries
    if len(query.split()) <= 2:
        return format_results(results)

    # Use reranking for everything else
    return retrieve_and_rerank(query, collection)
```

## Bottom Line

Cross-encoder reranking is the highest-impact optimization after basic setup:

1. **Install**: `pip install sentence-transformers`
2. **Use**: `cross-encoder/ms-marco-MiniLM-L-6-v2`
3. **Pipeline**: Retrieve 20 → Rerank → Return top 3
4. **Latency**: ~100-300ms added (worth it for accuracy)

Expected improvement: 20-40% better relevance ranking.

---

**Next**: [Query Expansion](05-query-expansion.md) - Catch different phrasings of the same question
