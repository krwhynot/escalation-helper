# How ChromaDB Works

Understanding vector search helps you debug when things go wrong and make informed optimization decisions.

## The Big Picture

When you search in ChromaDB, here's what actually happens:

```
User types: "cashier can't void an order"
                    ↓
        OpenAI embeds the query
        (converts text → 1536 numbers)
                    ↓
        ChromaDB finds the 3 closest
        vectors in the database
                    ↓
        Returns matching document chunks
        with distance scores
```

## What's an Embedding?

An embedding is just a list of numbers that represents the "meaning" of text. Think of it like GPS coordinates, but for concepts instead of locations.

```python
# Conceptually (not real numbers):
"void order"        → [0.82, -0.15, 0.43, ...]  # 1536 numbers
"cancel transaction" → [0.79, -0.12, 0.41, ...]  # Similar numbers!
"weather forecast"   → [-0.31, 0.67, -0.22, ...] # Very different numbers
```

Similar meanings = similar numbers = close together in "vector space"

## Why Searches Sometimes Return Irrelevant Results

### Problem 1: Everything Has a Distance

ChromaDB always returns `n_results` documents, even if none are relevant. If you ask "capital of mars" in a SQL troubleshooting database, you'll still get 3 results - they'll just be the 3 *least irrelevant* documents.

**Solution**: Filter by distance threshold ([see Quick Wins](02-quick-wins.md))

### Problem 2: Semantic Mismatch

The bi-encoder (OpenAI's embedding model) compresses complex meaning into a single vector. Sometimes it misses nuances:

```
Query: "order won't close"
Best match: Document about "closing the register"
Actual need: Document about "completing a sale"
```

**Solution**: Cross-encoder reranking ([see Reranking Guide](04-cross-encoder-reranking.md))

### Problem 3: Vocabulary Gap

Your users might say "void" but your docs say "cancel". Embeddings help with synonyms, but they're not perfect.

**Solution**: Query expansion ([see Query Expansion](05-query-expansion.md))

## The HNSW Algorithm (Simplified)

ChromaDB doesn't actually compare your query to every single document - that would be too slow. Instead, it uses HNSW (Hierarchical Navigable Small World), a clever algorithm that builds a graph:

```
Layer 2 (sparse):     A -------- B -------- C
                       \        /
Layer 1 (medium):    A -- D -- B -- E -- C
                      |    |    |    |    |
Layer 0 (dense):    A-F-D-G-B-H-E-I-C-J-K
```

- Search starts at the top layer (fast, coarse)
- Navigates down to find the neighborhood
- Searches thoroughly at the bottom layer

This is why HNSW parameters matter for large datasets - they control how connected and searchable this graph is.

## Distance Metrics Explained

ChromaDB supports three ways to measure "closeness":

### L2 (Euclidean Distance) - Default
- Measures straight-line distance between points
- Like measuring with a ruler in vector space
- Values: 0 = identical, larger = more different
- Problem: Numbers aren't intuitive (what does 1.2 mean?)

### Cosine Distance - Recommended for Text
- Measures the angle between vectors
- Ignores magnitude, focuses on direction
- Values: 0 = identical, 1 = unrelated, 2 = opposite
- Much more interpretable for text

### Inner Product
- Dot product of vectors
- Used in recommendation systems
- For normalized vectors (like ada-002), equals cosine similarity

**For OpenAI ada-002 embeddings**: All three produce the same ranking because the embeddings are normalized. But cosine gives you interpretable scores.

## The Embedding → Storage → Query Flow

### Ingestion (One Time)
```python
# 1. Load your documents
documents = ["How to void an order...", "Fixing register errors..."]

# 2. ChromaDB calls OpenAI to embed each chunk
# (This happens automatically when you add documents)
collection.add(
    documents=documents,
    ids=["doc1", "doc2"]
)

# 3. Embeddings are stored in the HNSW index
# Ready for searching!
```

### Query Time (Every Search)
```python
# 1. User enters a query
query = "cashier can't void order"

# 2. ChromaDB embeds the query (OpenAI API call)
# 3. Finds nearest neighbors in HNSW index
# 4. Returns documents + distances

results = collection.query(
    query_texts=[query],
    n_results=3
)

# results['documents'][0] = ["How to void an order...", ...]
# results['distances'][0] = [0.23, 0.45, 0.67]  # Lower = more relevant
```

## Understanding Distance Scores

When ChromaDB returns distances, here's how to interpret them (for cosine distance):

| Distance | Meaning | Should You Use It? |
|----------|---------|-------------------|
| 0.0 - 0.2 | Excellent match | Definitely yes |
| 0.2 - 0.35 | Good match | Probably yes |
| 0.35 - 0.5 | Okay match | Maybe |
| 0.5 - 0.7 | Weak match | Probably not |
| 0.7+ | Poor match | No |

## Bottom Line

- ChromaDB converts text to numbers (embeddings) and finds similar numbers
- It always returns results, even if none are good - you need to filter
- The bi-encoder is fast but imperfect - reranking helps
- For text embeddings, use cosine distance for interpretable scores
- HNSW makes search fast by building a navigable graph

---

**Next**: [Quick Wins](02-quick-wins.md) - Simple changes you can make today
