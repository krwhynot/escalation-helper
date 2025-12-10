# Quick Wins

Changes you can implement today with minimal effort and high impact.

## 1. Switch to Cosine Distance

**Current Problem**: You're using L2 (default), which gives unintuitive distance scores.

**Solution**: Use cosine distance for better interpretability.

### Why Cosine is Better for Text

```python
# L2 distances (hard to interpret):
"void order" vs "cancel transaction" = 0.547  # Is this good?
"void order" vs "weather forecast" = 1.823    # How much worse?

# Cosine distances (intuitive):
"void order" vs "cancel transaction" = 0.15   # 85% similar!
"void order" vs "weather forecast" = 0.72     # Only 28% similar
```

### Implementation

Update your `ingest.py` collection creation:

```python
# Before (default L2):
collection = client.create_collection(
    name=config.COLLECTION_NAME,
    embedding_function=openai_ef,
    metadata={"description": "Escalation Helper knowledge base"}
)

# After (cosine distance):
collection = client.create_collection(
    name=config.COLLECTION_NAME,
    embedding_function=openai_ef,
    metadata={
        "hnsw:space": "cosine",  # This is the key change!
        "description": "Escalation Helper knowledge base"
    }
)
```

**Important**: You must delete and re-ingest your documents after this change. The distance metric is locked at collection creation.

```bash
# Delete existing database and re-ingest
rm -rf chroma_db/
python ingest.py
```

---

## 2. Add Distance Threshold Filtering

**Current Problem**: ChromaDB always returns 3 results, even for irrelevant queries.

**Solution**: Filter out results with poor distance scores.

### Recommended Thresholds (Cosine Distance)

| Threshold | Use Case |
|-----------|----------|
| < 0.25 | High precision - only confident matches |
| < 0.35 | Balanced - good for most apps |
| **< 0.40** | **Recommended starting point** |
| < 0.50 | High recall - include borderline matches |

### Implementation

Update your `app.py` search function:

```python
def search_knowledge_base(query, collection, n_results=10, distance_threshold=0.40):
    """
    Search for relevant content with distance filtering.

    Args:
        query: User's search query
        collection: ChromaDB collection
        n_results: Candidates to retrieve (get more than you need)
        distance_threshold: Maximum distance to accept (0.4 = 60% similar)

    Returns:
        List of relevant results, or empty list if none qualify
    """
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )

    matches = []
    if results['documents'] and results['documents'][0]:
        for i, doc in enumerate(results['documents'][0]):
            distance = results['distances'][0][i]

            # Filter by threshold
            if distance <= distance_threshold:
                matches.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i],
                    'distance': distance,
                    'similarity_pct': round((1 - distance) * 100, 1)
                })

    return matches
```

### Handle "No Results" Gracefully

```python
def generate_response(query, collection):
    """Generate response with graceful no-results handling."""
    matches = search_knowledge_base(query, collection)

    if not matches:
        return {
            'success': False,
            'message': (
                f"I couldn't find relevant documentation for: '{query}'\n\n"
                "Try:\n"
                "- Using different terms (e.g., 'void' vs 'cancel')\n"
                "- Being more specific about the problem\n"
                "- Describing the error message you're seeing"
            ),
            'results': []
        }

    # Continue with normal LLM response generation...
    return {
        'success': True,
        'results': matches
    }
```

---

## 3. Improve Relevance Display

**Current Problem**: Your thresholds are arbitrary (0.5/0.8) and based on L2.

**Solution**: Update for cosine distance with meaningful labels.

### Implementation

```python
def get_relevance_info(distance):
    """
    Convert cosine distance to user-friendly relevance info.

    Args:
        distance: Cosine distance (0 = identical, 1 = unrelated)

    Returns:
        Tuple of (css_class, label, emoji, percentage)
    """
    similarity_pct = round((1 - distance) * 100, 1)

    if distance < 0.2:
        return ("excellent", "Excellent Match", "🎯", similarity_pct)
    elif distance < 0.35:
        return ("good", "Good Match", "✓", similarity_pct)
    elif distance < 0.5:
        return ("fair", "Fair Match", "~", similarity_pct)
    else:
        return ("weak", "Weak Match", "?", similarity_pct)


# Usage in Streamlit:
for match in matches:
    css_class, label, emoji, pct = get_relevance_info(match['distance'])
    st.markdown(f"**{emoji} {label}** ({pct}% similar)")
    st.markdown(match['content'])
```

---

## 4. Convert Distance to Percentage

Users understand "85% similar" better than "distance 0.15".

```python
def distance_to_similarity(cosine_distance):
    """
    Convert cosine distance to a 0-100% similarity score.

    Cosine distance ranges from 0 (identical) to 2 (opposite).
    We map this to 0-100% where 100% = identical.
    """
    # Simple conversion: similarity = 1 - distance
    similarity = (1 - cosine_distance) * 100
    return max(0, min(100, similarity))  # Clamp to 0-100

# Examples:
# distance 0.15 → 85% similar
# distance 0.35 → 65% similar
# distance 0.50 → 50% similar
```

---

## 5. Retrieve More, Show Less

**Insight**: Retrieve more candidates than you need, then filter to the best ones.

```python
# Before: Get exactly 3
results = collection.query(query_texts=[query], n_results=3)

# After: Get 10, filter to best 3
results = collection.query(query_texts=[query], n_results=10)
filtered = [r for r in results if r['distance'] < 0.40][:3]
```

This gives the filtering logic more candidates to work with.

---

## Complete Quick Wins Implementation

Here's everything together:

```python
# config.py - Add new settings
DISTANCE_THRESHOLD = 0.40  # Maximum cosine distance to accept
RETRIEVE_K = 10            # Candidates to retrieve
RETURN_K = 3               # Results to show user


# ingest.py - Update collection creation
collection = client.create_collection(
    name=config.COLLECTION_NAME,
    embedding_function=openai_ef,
    metadata={
        "hnsw:space": "cosine",
        "description": "Escalation Helper knowledge base"
    }
)


# app.py - Updated search function
def search_knowledge_base(query, collection):
    """Search with filtering and relevance scoring."""
    results = collection.query(
        query_texts=[query],
        n_results=config.RETRIEVE_K,
        include=["documents", "metadatas", "distances"]
    )

    matches = []
    if results['documents'] and results['documents'][0]:
        for i, doc in enumerate(results['documents'][0]):
            distance = results['distances'][0][i]

            if distance <= config.DISTANCE_THRESHOLD:
                similarity = round((1 - distance) * 100, 1)
                matches.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i],
                    'distance': distance,
                    'similarity': similarity,
                    'relevance': get_relevance_label(distance)
                })

    return matches[:config.RETURN_K]


def get_relevance_label(distance):
    """Get human-readable relevance label."""
    if distance < 0.2:
        return "Excellent"
    elif distance < 0.35:
        return "Good"
    elif distance < 0.5:
        return "Fair"
    return "Weak"
```

---

## Bottom Line

These quick wins take about 30 minutes total and provide:

1. **Cosine distance**: Interpretable scores (0-1 range)
2. **Threshold filtering**: No more irrelevant results
3. **Better UX**: Percentage similarity users understand
4. **Graceful failures**: Helpful "no results" messages

After implementing these, you'll have a much more reliable search experience. For even better accuracy, see the [Cross-Encoder Reranking](04-cross-encoder-reranking.md) guide.

---

**Next**: [HNSW Parameters](03-hnsw-parameters.md) - Deep dive into index tuning
