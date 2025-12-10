# Query Expansion

Query expansion generates variations of the user's query to catch documents that use different terminology. If your user says "void" but your docs say "cancel," query expansion bridges that gap.

## The Problem

Vector search handles synonyms better than keyword search, but it's not perfect:

```
User query: "order won't close"
Docs use: "complete sale", "finalize transaction", "close ticket"

Embedding might not connect "close" with "complete" or "finalize"
```

## Solution: Generate Query Variations

Use GPT to create alternative phrasings:

```
Original: "order won't close"
Variations:
- "cannot complete sale"
- "transaction stuck open"
- "how to finalize order"
```

Search with all of them, combine results.

## Implementation

### Basic Query Expansion

```python
import openai

def expand_query(query: str, num_variations: int = 3) -> list:
    """
    Generate query variations using GPT.

    Args:
        query: Original user query
        num_variations: Number of variations to generate

    Returns:
        List containing original query + variations
    """
    prompt = f"""You are a search query optimizer for SQL and database troubleshooting documentation.

Original query: "{query}"

Generate {num_variations} alternative phrasings that might help find relevant documentation.
Focus on:
- Different technical terms (e.g., "void" vs "cancel" vs "reverse")
- Different perspectives (symptom vs. solution vs. error message)
- Specific vs. general terms

Return ONLY the queries, one per line, no numbering or explanation."""

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You generate search query variations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )

        content = response.choices[0].message.content.strip()
        variations = [v.strip() for v in content.split('\n') if v.strip()]

        # Return original + variations
        return [query] + variations[:num_variations]

    except Exception as e:
        print(f"Query expansion failed: {e}")
        return [query]  # Fall back to original only
```

### Multi-Query Search

```python
def multi_query_search(query: str, collection, k_per_query: int = 5) -> list:
    """
    Search with multiple query variations and deduplicate results.

    Args:
        query: Original user query
        collection: ChromaDB collection
        k_per_query: Results to retrieve per query variation

    Returns:
        Deduplicated list of results sorted by best distance
    """
    # Generate query variations
    queries = expand_query(query, num_variations=3)
    print(f"Searching with: {queries}")

    # Search with all queries at once (ChromaDB supports batch queries)
    results = collection.query(
        query_texts=queries,
        n_results=k_per_query,
        include=["documents", "metadatas", "distances"]
    )

    # Deduplicate by document ID, keeping best distance
    seen = {}
    for query_idx in range(len(queries)):
        for doc_idx in range(len(results['ids'][query_idx])):
            doc_id = results['ids'][query_idx][doc_idx]
            distance = results['distances'][query_idx][doc_idx]

            if doc_id not in seen or distance < seen[doc_id]['distance']:
                seen[doc_id] = {
                    'id': doc_id,
                    'document': results['documents'][query_idx][doc_idx],
                    'metadata': results['metadatas'][query_idx][doc_idx],
                    'distance': distance,
                    'matched_query': queries[query_idx]
                }

    # Sort by distance (best first)
    unique_results = sorted(seen.values(), key=lambda x: x['distance'])

    return unique_results
```

### Combined with Reranking

For best results, combine query expansion with cross-encoder reranking:

```python
from sentence_transformers import CrossEncoder

cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')


def full_pipeline_search(query: str, collection) -> list:
    """
    Full search pipeline: expansion → retrieval → reranking.
    """
    # Step 1: Expand query
    queries = expand_query(query, num_variations=3)

    # Step 2: Retrieve candidates for all query variations
    results = collection.query(
        query_texts=queries,
        n_results=10,  # More candidates since we're reranking
        include=["documents", "metadatas", "distances"]
    )

    # Step 3: Deduplicate
    candidates = {}
    for query_idx in range(len(queries)):
        for doc_idx in range(len(results['ids'][query_idx])):
            doc_id = results['ids'][query_idx][doc_idx]
            distance = results['distances'][query_idx][doc_idx]

            if doc_id not in candidates or distance < candidates[doc_id]['distance']:
                candidates[doc_id] = {
                    'document': results['documents'][query_idx][doc_idx],
                    'metadata': results['metadatas'][query_idx][doc_idx],
                    'distance': distance
                }

    if not candidates:
        return []

    # Step 4: Rerank with cross-encoder (use original query)
    candidate_list = list(candidates.values())
    pairs = [[query, c['document']] for c in candidate_list]
    scores = cross_encoder.predict(pairs)

    for i, candidate in enumerate(candidate_list):
        candidate['cross_encoder_score'] = float(scores[i])

    # Step 5: Sort by cross-encoder score and return top 3
    reranked = sorted(candidate_list, key=lambda x: x['cross_encoder_score'], reverse=True)

    return reranked[:3]
```

## Alternative: HyDE (Hypothetical Document Embedding)

Instead of varying the query, generate a hypothetical answer and search with that. This works well when you know what format answers should be in.

```python
def hyde_search(query: str, collection) -> list:
    """
    HyDE: Generate hypothetical answer, embed it, search.

    Better for questions where the answer format is predictable.
    """
    # Generate hypothetical answer
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a SQL troubleshooting expert. "
                    "Answer questions concisely as if reading from documentation. "
                    "Include specific SQL commands when relevant."
                )
            },
            {"role": "user", "content": query}
        ],
        temperature=0.3,
        max_tokens=300
    )

    hypothetical_answer = response.choices[0].message.content
    print(f"HyDE generated: {hypothetical_answer[:100]}...")

    # Search using the hypothetical answer
    results = collection.query(
        query_texts=[hypothetical_answer],
        n_results=5
    )

    return results
```

### When to Use HyDE vs Query Expansion

| Approach | Best For | Example |
|----------|----------|---------|
| Query Expansion | Varied terminology | "void" vs "cancel" vs "reverse" |
| HyDE | Predictable answer format | SQL troubleshooting with code examples |
| Both | Maximum recall | Complex queries where you're not sure |

## Cost and Latency Analysis

### Query Expansion
- **API calls**: 1 per query (gpt-4o-mini)
- **Cost**: ~$0.00015 per expansion
- **Latency**: 200-500ms

### HyDE
- **API calls**: 1 per query (gpt-4o-mini)
- **Cost**: ~$0.0003 per query (longer response)
- **Latency**: 300-700ms

### Full Pipeline (Expansion + Retrieval + Reranking)
- **API calls**: 1 (expansion) + 1 (embedding via ChromaDB)
- **Cost**: ~$0.0005 per query total
- **Latency**: 500-1000ms total

For a team of 10 users doing 100 queries/day:
- Monthly cost: ~$1.50 (negligible)
- Worth it for better accuracy

## Caching Query Expansions

For common queries, cache the expansions:

```python
import functools

@functools.lru_cache(maxsize=1000)
def cached_expand_query(query: str) -> tuple:
    """Cache query expansions for repeated queries."""
    variations = expand_query(query, num_variations=3)
    return tuple(variations)  # Tuples are hashable for caching

def search_with_cached_expansion(query: str, collection) -> list:
    """Search using cached query expansions."""
    queries = list(cached_expand_query(query))

    results = collection.query(
        query_texts=queries,
        n_results=5
    )

    return results
```

## Domain-Specific Expansion Prompts

Customize the expansion prompt for better results:

```python
def expand_query_sql(query: str) -> list:
    """SQL-specific query expansion."""
    prompt = f"""You are a search optimizer for HungerRush POS troubleshooting documentation.

Query: "{query}"

Generate 3 alternative search queries. Consider:
- POS terminology: "void", "comp", "refund", "close", "settle"
- Database terms: "SQL", "query", "table", "column", "transaction"
- Error symptoms vs solutions
- Revention-specific table names if relevant

Return ONLY the queries, one per line."""

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=150
    )

    variations = response.choices[0].message.content.strip().split('\n')
    return [query] + [v.strip() for v in variations if v.strip()][:3]
```

## When to Skip Query Expansion

Query expansion adds latency and cost. Consider skipping when:

1. **Very specific queries**: "SELECT * FROM orders WHERE order_id = 123"
2. **High confidence results**: If first result has distance < 0.15
3. **Known exact matches**: User searching for specific error codes
4. **Latency critical**: Real-time autocomplete

```python
def smart_search(query: str, collection) -> list:
    """Use expansion only when beneficial."""

    # Skip for very specific queries
    if query.upper().startswith(('SELECT', 'UPDATE', 'INSERT', 'DELETE')):
        return simple_search(query, collection)

    # Quick search first
    quick_results = collection.query(query_texts=[query], n_results=3)

    # If top result is excellent, skip expansion
    if quick_results['distances'][0][0] < 0.15:
        return format_results(quick_results)

    # Use expansion for uncertain results
    return multi_query_search(query, collection)
```

## Bottom Line

Query expansion bridges the vocabulary gap between users and documentation:

1. **Use gpt-4o-mini** for fast, cheap query variations
2. **Combine with reranking** for best results
3. **Cache common queries** to reduce latency
4. **Skip for high-confidence** results to save time

Expected improvement: 10-20% better recall for queries with terminology mismatches.

---

**Next**: [Metadata Filtering](06-metadata-filtering.md) - Let users narrow their search
