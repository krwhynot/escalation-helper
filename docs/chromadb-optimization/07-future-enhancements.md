# Future Enhancements

These are advanced techniques to consider once you've implemented the basics. They require more effort but can provide significant improvements for specific use cases.

## 1. Hybrid Search (BM25 + Vector)

### The Idea

Combine keyword matching (BM25) with semantic search (vectors):
- **BM25**: Catches exact term matches, acronyms, specific codes
- **Vector**: Catches semantic meaning, synonyms, paraphrases

### When It Helps

- User searches for error code "ERR-5431" → BM25 finds exact match
- User searches for "order not working" → Vector finds semantic matches
- Combined: Better coverage than either alone

### Implementation Sketch

```python
from rank_bm25 import BM25Okapi
import numpy as np

class HybridSearcher:
    def __init__(self, collection, documents):
        self.collection = collection
        self.documents = documents

        # Build BM25 index
        tokenized = [doc.lower().split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized)

    def search(self, query: str, k: int = 10, alpha: float = 0.5) -> list:
        """
        Hybrid search with adjustable weighting.

        Args:
            query: Search query
            k: Number of results
            alpha: Weight for vector search (1-alpha for BM25)
        """
        # BM25 scores (keyword)
        bm25_scores = self.bm25.get_scores(query.lower().split())
        bm25_normalized = bm25_scores / (bm25_scores.max() + 1e-6)

        # Vector scores (semantic)
        results = self.collection.query(
            query_texts=[query],
            n_results=len(self.documents)
        )

        # Convert distances to scores (lower distance = higher score)
        vector_scores = np.zeros(len(self.documents))
        for i, doc_id in enumerate(results['ids'][0]):
            idx = int(doc_id.split('_')[-1])  # Extract index from ID
            distance = results['distances'][0][i]
            vector_scores[idx] = 1 - distance

        # Combine scores
        combined = alpha * vector_scores + (1 - alpha) * bm25_normalized

        # Get top k
        top_indices = combined.argsort()[-k:][::-1]

        return [
            {
                'document': self.documents[i],
                'combined_score': combined[i],
                'vector_score': vector_scores[i],
                'bm25_score': bm25_normalized[i]
            }
            for i in top_indices
        ]
```

### LangChain Alternative

```python
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_chroma import Chroma

# Create retrievers
bm25_retriever = BM25Retriever.from_documents(documents)
bm25_retriever.k = 10

chroma_retriever = vectorstore.as_retriever(search_kwargs={"k": 10})

# Combine with equal weights
ensemble = EnsembleRetriever(
    retrievers=[bm25_retriever, chroma_retriever],
    weights=[0.5, 0.5]
)

results = ensemble.invoke("how to void an order")
```

### Effort & Impact
- **Effort**: High (new dependencies, index management)
- **Impact**: Medium-High (especially for exact match queries)

---

## 2. Embedding Fine-Tuning

### The Idea

Train custom embeddings specifically for SQL troubleshooting queries.

### When It Helps

- Generic embeddings miss domain-specific relationships
- "Void" and "cancel" should be closer than generic embeddings make them
- Your data has unique terminology

### Requirements

- Labeled pairs: (query, relevant_document) - need ~100+ pairs minimum
- Training infrastructure (GPU recommended)
- Sentence-transformers library

### Implementation Sketch

```python
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

# Training data: (query, positive_doc, negative_doc) triplets
train_examples = [
    InputExample(
        texts=["how to void order",
               "To void an order, use UPDATE orders SET status='voided'...",
               "The weather forecast for today shows sunny skies..."]
    ),
    # Add more examples...
]

# Load base model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Create dataloader
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)

# Use triplet loss
train_loss = losses.TripletLoss(model=model)

# Fine-tune
model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=3,
    warmup_steps=100,
    output_path='./fine-tuned-sql-embeddings'
)

# Use the fine-tuned model
# Replace OpenAI embeddings with your custom model
```

### Collecting Training Data

Ways to get labeled pairs:

1. **Click data**: Log which results users click on
2. **Manual labeling**: Have team members mark relevant/irrelevant
3. **Synthetic generation**: Use GPT to generate query-answer pairs from your docs

### Effort & Impact
- **Effort**: High (need data, training time)
- **Impact**: High (can significantly improve domain-specific relevance)

---

## 3. Embedding Adapters

### The Idea

Instead of fine-tuning the whole model, learn a lightweight transformation on top of ada-002.

### When It Helps

- Want some customization without full fine-tuning
- Limited training data
- Want to use OpenAI embeddings but improve domain fit

### Implementation Sketch

```python
import numpy as np
from sklearn.linear_model import LogisticRegression

class EmbeddingAdapter:
    """Learn a linear transformation on embeddings."""

    def __init__(self):
        self.transformation = None

    def fit(self, positive_pairs: list, negative_pairs: list):
        """
        Train adapter on labeled pairs.

        positive_pairs: [(query_emb, relevant_doc_emb), ...]
        negative_pairs: [(query_emb, irrelevant_doc_emb), ...]
        """
        # Create training data
        X = []  # Concatenated embeddings
        y = []  # 1 for relevant, 0 for not

        for q_emb, d_emb in positive_pairs:
            X.append(np.concatenate([q_emb, d_emb]))
            y.append(1)

        for q_emb, d_emb in negative_pairs:
            X.append(np.concatenate([q_emb, d_emb]))
            y.append(0)

        # Train simple classifier
        self.model = LogisticRegression()
        self.model.fit(X, y)

    def score(self, query_emb, doc_emb) -> float:
        """Score a query-document pair."""
        features = np.concatenate([query_emb, doc_emb]).reshape(1, -1)
        return self.model.predict_proba(features)[0, 1]
```

### Effort & Impact
- **Effort**: Medium (simpler than full fine-tuning)
- **Impact**: Medium (improvements depend on training data quality)

---

## 4. Query Caching

### The Idea

Cache embeddings and results for common queries.

### Implementation

```python
from functools import lru_cache
import hashlib
import json

class CachedSearcher:
    def __init__(self, collection):
        self.collection = collection
        self.result_cache = {}

    def _cache_key(self, query: str, filters: dict) -> str:
        """Generate cache key from query and filters."""
        data = {"query": query, "filters": filters}
        return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()

    def search(self, query: str, filters: dict = None, use_cache: bool = True) -> list:
        """Search with optional caching."""
        cache_key = self._cache_key(query, filters or {})

        if use_cache and cache_key in self.result_cache:
            return self.result_cache[cache_key]

        results = self.collection.query(
            query_texts=[query],
            n_results=10,
            where=filters
        )

        # Cache for common queries
        self.result_cache[cache_key] = results

        return results

    def clear_cache(self):
        """Clear the result cache."""
        self.result_cache = {}
```

### Redis-Based Caching (Production)

```python
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379)

def cached_search(query: str, collection, ttl: int = 3600):
    """Search with Redis caching."""
    cache_key = f"search:{hashlib.md5(query.encode()).hexdigest()}"

    # Check cache
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # Execute search
    results = collection.query(query_texts=[query], n_results=10)

    # Cache with TTL
    redis_client.setex(cache_key, ttl, json.dumps(results))

    return results
```

### Effort & Impact
- **Effort**: Low-Medium
- **Impact**: High for latency, low for accuracy

---

## 5. Analytics & Feedback Loop

### The Idea

Track what works and what doesn't to continuously improve.

### What to Track

```python
import datetime
import json

class SearchAnalytics:
    def __init__(self, log_file: str = "search_logs.jsonl"):
        self.log_file = log_file

    def log_search(self, query: str, results: list, user_id: str = None):
        """Log a search event."""
        event = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "query": query,
            "num_results": len(results),
            "top_result_distance": results[0]['distance'] if results else None,
            "result_sources": [r['metadata'].get('source') for r in results[:3]],
            "user_id": user_id
        }

        with open(self.log_file, 'a') as f:
            f.write(json.dumps(event) + '\n')

    def log_feedback(self, query: str, result_index: int, helpful: bool):
        """Log user feedback on a result."""
        event = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "type": "feedback",
            "query": query,
            "result_index": result_index,
            "helpful": helpful
        }

        with open(self.log_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
```

### Streamlit Feedback UI

```python
def display_result_with_feedback(result: dict, index: int, query: str):
    """Display result with feedback buttons."""
    st.markdown(result['content'])

    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"👍 Helpful", key=f"helpful_{index}"):
            analytics.log_feedback(query, index, helpful=True)
            st.success("Thanks for the feedback!")
    with col2:
        if st.button(f"👎 Not helpful", key=f"not_helpful_{index}"):
            analytics.log_feedback(query, index, helpful=False)
            st.info("Thanks, we'll use this to improve!")
```

### Analyzing Logs

```python
import pandas as pd

def analyze_search_quality():
    """Generate insights from search logs."""
    logs = []
    with open("search_logs.jsonl") as f:
        for line in f:
            logs.append(json.loads(line))

    df = pd.DataFrame(logs)

    # Queries with no results
    no_results = df[df['num_results'] == 0]['query'].value_counts()
    print("Queries with no results:\n", no_results.head(10))

    # Low confidence results
    low_confidence = df[df['top_result_distance'] > 0.5]['query'].value_counts()
    print("\nQueries with poor matches:\n", low_confidence.head(10))

    # Most common queries
    print("\nMost common queries:\n", df['query'].value_counts().head(20))
```

### Effort & Impact
- **Effort**: Low-Medium
- **Impact**: High (identifies gaps, guides improvements)

---

## Implementation Roadmap

Based on effort vs impact, here's a suggested order:

| Phase | Enhancement | When to Implement |
|-------|-------------|-------------------|
| 1 | Query Caching | When you have repeat queries |
| 2 | Analytics | After basic search is working |
| 3 | Hybrid Search | When exact match queries fail |
| 4 | Embedding Adapters | When you have feedback data |
| 5 | Full Fine-Tuning | When you have 100+ labeled pairs |

## Bottom Line

These advanced techniques are powerful but require investment:

1. **Start simple**: Get the basics working first
2. **Collect data**: Analytics enable all future improvements
3. **Iterate based on evidence**: Don't add complexity without measuring impact

Most applications never need full fine-tuning - the simpler techniques often provide 80% of the benefit.

---

**Next**: [Implementation Priority](08-implementation-priority.md) - Putting it all together
