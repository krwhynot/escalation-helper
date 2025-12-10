# HNSW Parameters Deep Dive

HNSW (Hierarchical Navigable Small World) is the algorithm ChromaDB uses for fast approximate nearest neighbor search. For most use cases, the defaults are fine - but here's what everything does if you need to tune.

## The Short Answer

**For datasets under 500 documents**: Keep the defaults. Your time is better spent on reranking and query expansion.

**When to tune HNSW**:
- You have 10,000+ documents AND
- You're seeing recall issues (missing relevant results) OR
- Search is too slow

## Parameters Overview

| Parameter | Default | Can Change After Creation? | When to Tune |
|-----------|---------|---------------------------|--------------|
| `hnsw:space` | l2 | No | Always set to `cosine` for text |
| `hnsw:M` | 16 | No | Rarely - only for huge datasets |
| `hnsw:construction_ef` | 100 | No | Rarely - only if index quality issues |
| `hnsw:search_ef` | 100 | Yes | Sometimes - if missing results |
| `hnsw:num_threads` | CPU count | Yes | If you want to limit CPU usage |
| `hnsw:batch_size` | 100 | Yes | Rarely |
| `hnsw:resize_factor` | 1.2 | Yes | Never |
| `hnsw:sync_threshold` | 1000 | Yes | Rarely |

## Parameter Deep Dives

### `hnsw:space` - Distance Metric

**What it does**: Controls how "closeness" is calculated.

**Options**:
- `l2` (default): Euclidean distance squared
- `cosine`: Angle between vectors (recommended for text)
- `ip`: Inner product

**Recommendation**: Always use `cosine` for text embeddings.

```python
collection = client.create_collection(
    name="my_collection",
    metadata={"hnsw:space": "cosine"}
)
```

**Cannot be changed after creation** - you must delete and recreate the collection.

---

### `hnsw:M` - Graph Connectivity

**What it does**: Maximum number of neighbors each node connects to in the graph.

**Trade-off**:
- Higher M = denser graph = better recall = more memory = slower build
- Lower M = sparser graph = faster build = less memory = might miss results

**Defaults and recommendations**:

| Dataset Size | Recommended M |
|--------------|---------------|
| < 1,000 docs | 16 (default) |
| 1,000 - 10,000 | 16-32 |
| 10,000 - 100,000 | 32-48 |
| 100,000+ | 48-64 |

**For Escalation Helper**: Keep default 16. You have ~17 documents (maybe 100-500 chunks), nowhere near needing adjustment.

```python
# Only if you have a large dataset:
collection = client.create_collection(
    name="large_collection",
    metadata={
        "hnsw:space": "cosine",
        "hnsw:M": 32  # Increased for larger dataset
    }
)
```

---

### `hnsw:construction_ef` - Build Quality

**What it does**: Size of the candidate list when building the index. Higher values mean the algorithm considers more options when deciding where to place each vector.

**Trade-off**:
- Higher = better quality index = slower build time
- Lower = faster build = potentially worse recall

**Default**: 100 (good balance)

**When to increase**: If you've tuned everything else and still have recall issues, try 150-200.

```python
collection = client.create_collection(
    name="high_quality_index",
    metadata={
        "hnsw:space": "cosine",
        "hnsw:construction_ef": 200  # Higher quality, slower build
    }
)
```

**For Escalation Helper**: Keep default. Build time isn't a concern with your dataset size.

---

### `hnsw:search_ef` - Query Quality

**What it does**: Size of the candidate list during search. Higher values explore more of the graph before returning results.

**Trade-off**:
- Higher = better recall = slower queries
- Lower = faster queries = might miss results

**Default**: 100

**This is the one parameter worth tuning for small datasets** if you're missing results.

```python
# At collection creation:
collection = client.create_collection(
    name="my_collection",
    metadata={
        "hnsw:space": "cosine",
        "hnsw:search_ef": 150  # Explore more, find better results
    }
)

# Or update after creation (this one CAN be changed):
collection.modify(metadata={"hnsw:search_ef": 200})
```

**Must be >= n_results**: If you're retrieving 20 candidates, search_ef must be at least 20.

**Recommendations**:

| Situation | search_ef Value |
|-----------|-----------------|
| Default, works fine | 100 |
| Missing some relevant results | 150-200 |
| Really need high recall | 300-500 |
| Maximum recall, latency not critical | 1000 |

---

### `hnsw:num_threads` - Parallelization

**What it does**: Number of threads for index operations.

**Default**: Number of CPUs on the system

**When to change**: If running on shared infrastructure and want to limit CPU usage.

```python
collection = client.create_collection(
    name="my_collection",
    metadata={
        "hnsw:space": "cosine",
        "hnsw:num_threads": 4  # Limit to 4 threads
    }
)
```

---

### `hnsw:batch_size` - Batch Processing

**What it does**: Number of vectors processed per batch during operations.

**Default**: 100

**When to change**: Almost never. Only if you have memory constraints during large batch inserts.

---

### `hnsw:resize_factor` - Index Growth

**What it does**: When the index needs more capacity, it grows by this factor.

**Default**: 1.2 (20% growth each time)

**When to change**: Never. The default is fine.

---

### `hnsw:sync_threshold` - Persistence

**What it does**: How often to sync changes to disk (for persistent storage).

**Default**: 1000 operations

**When to change**: Rarely. Lower values mean more frequent writes (safer but slower).

---

## Complete Configuration Example

Here's an optimized configuration for a medium-sized SQL troubleshooting database:

```python
import chromadb
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(path="./chroma_db")

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=config.OPENAI_API_KEY,
    model_name="text-embedding-ada-002"
)

# Optimized collection for text search
collection = client.create_collection(
    name="sql_troubleshooting",
    embedding_function=openai_ef,
    metadata={
        # Distance metric - MUST set for text
        "hnsw:space": "cosine",

        # Keep defaults for small dataset
        "hnsw:M": 16,
        "hnsw:construction_ef": 100,

        # Slightly higher for better recall
        "hnsw:search_ef": 150,

        # Application metadata
        "description": "SQL troubleshooting knowledge base"
    }
)
```

## How to Know if You Have Recall Issues

Signs that HNSW tuning might help:

1. **User reports missing obvious results**: "I searched for 'void order' but it didn't find the void order documentation"

2. **Inconsistent results**: Same query returns different results on different runs

3. **Relevant docs exist but aren't returned**: You know doc X should match, but it's not in the top results

**Before tuning HNSW, try these first**:
1. Increase `n_results` (retrieve more candidates)
2. Add distance threshold filtering
3. Implement cross-encoder reranking

These usually solve "missing results" better than HNSW tuning.

## Changing Parameters on Existing Collections

**Can change anytime**:
```python
collection.modify(metadata={
    "hnsw:search_ef": 200,
    "hnsw:num_threads": 4
})
```

**Cannot change (must recreate collection)**:
- `hnsw:space`
- `hnsw:M`
- `hnsw:construction_ef`

To change locked parameters:
```bash
# 1. Delete the collection
rm -rf chroma_db/

# 2. Update your ingest.py with new parameters

# 3. Re-ingest all documents
python ingest.py
```

## Bottom Line

For Escalation Helper with <500 documents:

1. **Set `hnsw:space` to `cosine`** - This is the only required change
2. **Keep M, construction_ef at defaults** - Your dataset is too small to benefit from tuning
3. **Maybe increase search_ef to 150** - If you're missing results after implementing other optimizations

Your time is better spent on:
- Distance threshold filtering (Quick Wins)
- Cross-encoder reranking (next guide)
- Better chunking strategies

---

**Next**: [Cross-Encoder Reranking](04-cross-encoder-reranking.md) - The biggest accuracy improvement
