# Metadata Filtering

Metadata filtering lets users narrow their search to specific categories, document types, or other attributes. It's like adding faceted search to your vector database.

## Current State

Your current metadata per chunk:
```python
{
    "source": "sql_reference.md",
    "file_path": "/full/path/to/file.md",
    "chunk_index": 0
}
```

This is minimal. Let's expand it.

## Recommended Metadata Schema

```python
{
    # Existing fields
    "source": "sql_reference.md",
    "file_path": "/full/path/to/file.md",
    "chunk_index": 0,

    # New fields for filtering
    "category": "troubleshooting",       # troubleshooting, reference, tutorial, faq
    "problem_type": "void_transaction",  # specific problem area
    "sql_dialect": "postgresql",         # mysql, postgresql, mssql
    "difficulty": "intermediate",        # beginner, intermediate, advanced
    "doc_type": "query",                 # query, explanation, procedure

    # For hybrid search (future)
    "keywords": "void cancel refund order transaction"
}
```

## Updating Your Ingest Script

### Option 1: Manual Category Assignment

If you have few documents, manually categorize them:

```python
# ingest.py

# Define categories per source file
FILE_CATEGORIES = {
    "sql_reference.md": {
        "category": "reference",
        "doc_type": "query"
    },
    "05 - Query Validation Report.md": {
        "category": "validation",
        "doc_type": "report"
    },
    "06 - Database Table Quick Reference.md": {
        "category": "reference",
        "doc_type": "explanation"
    },
    "09 - Corrected SQL Queries.md": {
        "category": "troubleshooting",
        "doc_type": "query"
    }
}


def get_chunk_metadata(filename: str, file_path: str, chunk_index: int) -> dict:
    """Build metadata for a chunk."""
    base_metadata = {
        "source": filename,
        "file_path": file_path,
        "chunk_index": chunk_index
    }

    # Add file-level categories
    if filename in FILE_CATEGORIES:
        base_metadata.update(FILE_CATEGORIES[filename])
    else:
        base_metadata["category"] = "general"
        base_metadata["doc_type"] = "unknown"

    return base_metadata
```

### Option 2: LLM-Based Categorization

For larger datasets, use GPT to categorize during ingestion:

```python
import openai

def categorize_chunk(chunk_text: str) -> dict:
    """Use GPT to categorize a chunk."""
    prompt = f"""Analyze this documentation chunk and provide metadata.

Chunk:
{chunk_text[:1000]}

Return a JSON object with these fields:
- category: one of [troubleshooting, reference, tutorial, faq, procedure]
- problem_type: brief description of the problem addressed (or "general" if not applicable)
- difficulty: one of [beginner, intermediate, advanced]
- keywords: 3-5 relevant keywords separated by spaces

Return ONLY valid JSON, no explanation."""

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=150
    )

    import json
    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        return {
            "category": "general",
            "problem_type": "general",
            "difficulty": "intermediate",
            "keywords": ""
        }
```

### Option 3: Rule-Based Extraction

Use patterns in your content:

```python
import re

def extract_metadata_from_content(chunk_text: str, filename: str) -> dict:
    """Extract metadata based on content patterns."""
    metadata = {
        "category": "general",
        "doc_type": "explanation"
    }

    # Detect SQL queries
    if re.search(r'\bSELECT\b|\bUPDATE\b|\bINSERT\b|\bDELETE\b', chunk_text, re.IGNORECASE):
        metadata["doc_type"] = "query"

    # Detect troubleshooting content
    troubleshooting_keywords = ["error", "fix", "issue", "problem", "solution", "resolve"]
    if any(kw in chunk_text.lower() for kw in troubleshooting_keywords):
        metadata["category"] = "troubleshooting"

    # Detect procedures
    if re.search(r'step \d|1\.|first,', chunk_text.lower()):
        metadata["doc_type"] = "procedure"

    # Detect specific problem types
    problem_patterns = {
        "void_transaction": r'\bvoid\b.*\border\b|\border\b.*\bvoid\b',
        "payment_issue": r'\bpayment\b|\bcredit card\b|\bcharge\b',
        "register_close": r'\bclose\b.*\bregister\b|\bend of day\b',
        "inventory": r'\binventory\b|\bstock\b'
    }

    for problem_type, pattern in problem_patterns.items():
        if re.search(pattern, chunk_text, re.IGNORECASE):
            metadata["problem_type"] = problem_type
            break
    else:
        metadata["problem_type"] = "general"

    return metadata
```

## ChromaDB Where Clause Syntax

### Basic Filtering

```python
# Filter by single field
results = collection.query(
    query_texts=["how to void order"],
    n_results=5,
    where={"category": "troubleshooting"}
)
```

### Multiple Conditions (AND)

```python
# All conditions must match
results = collection.query(
    query_texts=["slow query"],
    n_results=5,
    where={
        "category": "troubleshooting",
        "doc_type": "query"
    }
)
```

### $or Operator

```python
# Match any of the conditions
results = collection.query(
    query_texts=["transaction issue"],
    n_results=5,
    where={
        "$or": [
            {"problem_type": "void_transaction"},
            {"problem_type": "payment_issue"}
        ]
    }
)
```

### $and Operator

```python
# Explicit AND (same as default)
results = collection.query(
    query_texts=["help"],
    n_results=5,
    where={
        "$and": [
            {"category": "troubleshooting"},
            {"difficulty": "beginner"}
        ]
    }
)
```

### $in Operator (Multiple Values for One Field)

```python
# Match any value in the list
results = collection.query(
    query_texts=["database error"],
    n_results=5,
    where={
        "problem_type": {"$in": ["connection", "timeout", "deadlock"]}
    }
)
```

### $nin Operator (Exclude Values)

```python
# Exclude certain values
results = collection.query(
    query_texts=["general help"],
    n_results=5,
    where={
        "category": {"$nin": ["reference", "faq"]}
    }
)
```

### Comparison Operators

```python
# $eq, $ne, $gt, $gte, $lt, $lte
results = collection.query(
    query_texts=["advanced topics"],
    where={"difficulty": {"$eq": "advanced"}}
)

# Numeric comparisons
results = collection.query(
    query_texts=["recent additions"],
    where={"chunk_index": {"$lt": 5}}  # First 5 chunks only
)
```

### $contains for Text Search

```python
# Filter on document content
results = collection.query(
    query_texts=["performance issue"],
    where_document={"$contains": "VACUUM"}
)
```

## Streamlit UI Integration

### Simple Dropdown Filter

```python
import streamlit as st

def search_page():
    st.title("SQL Troubleshooting Search")

    # Category filter
    categories = ["All", "troubleshooting", "reference", "tutorial", "faq"]
    selected_category = st.selectbox("Category:", categories)

    # Difficulty filter
    difficulties = ["All", "beginner", "intermediate", "advanced"]
    selected_difficulty = st.selectbox("Difficulty:", difficulties)

    # Search input
    query = st.text_input("Search query:")

    if st.button("Search") and query:
        # Build where clause
        where_clause = {}

        if selected_category != "All":
            where_clause["category"] = selected_category

        if selected_difficulty != "All":
            where_clause["difficulty"] = selected_difficulty

        # Execute search
        results = collection.query(
            query_texts=[query],
            n_results=5,
            where=where_clause if where_clause else None
        )

        display_results(results)
```

### Multi-Select Filters

```python
def advanced_search_page():
    st.title("Advanced Search")

    # Multi-select categories
    all_categories = ["troubleshooting", "reference", "tutorial", "faq", "procedure"]
    selected_categories = st.multiselect(
        "Categories (select multiple):",
        all_categories,
        default=all_categories
    )

    # Problem type filter
    problem_types = [
        "void_transaction", "payment_issue", "register_close",
        "inventory", "reporting", "general"
    ]
    selected_problems = st.multiselect(
        "Problem types:",
        problem_types
    )

    query = st.text_input("Search query:")

    if st.button("Search") and query:
        # Build complex where clause
        conditions = []

        if selected_categories and len(selected_categories) < len(all_categories):
            conditions.append({
                "category": {"$in": selected_categories}
            })

        if selected_problems:
            conditions.append({
                "problem_type": {"$in": selected_problems}
            })

        where_clause = None
        if len(conditions) == 1:
            where_clause = conditions[0]
        elif len(conditions) > 1:
            where_clause = {"$and": conditions}

        results = collection.query(
            query_texts=[query],
            n_results=10,
            where=where_clause
        )

        display_results(results)
```

### Filter Summary Display

```python
def display_active_filters(where_clause: dict):
    """Show users what filters are active."""
    if not where_clause:
        st.info("Searching all documents")
        return

    filter_parts = []

    if "category" in where_clause:
        cat = where_clause["category"]
        if isinstance(cat, dict) and "$in" in cat:
            filter_parts.append(f"Categories: {', '.join(cat['$in'])}")
        else:
            filter_parts.append(f"Category: {cat}")

    if "problem_type" in where_clause:
        pt = where_clause["problem_type"]
        if isinstance(pt, dict) and "$in" in pt:
            filter_parts.append(f"Problem types: {', '.join(pt['$in'])}")
        else:
            filter_parts.append(f"Problem type: {pt}")

    if filter_parts:
        st.caption(f"Active filters: {' | '.join(filter_parts)}")
```

## Complete Example: Filtered Search Function

```python
def search_with_filters(
    query: str,
    collection,
    category: str = None,
    problem_type: str = None,
    difficulty: str = None,
    doc_type: str = None,
    n_results: int = 10
) -> list:
    """
    Search with optional metadata filters.

    Args:
        query: Search query
        collection: ChromaDB collection
        category: Optional category filter
        problem_type: Optional problem type filter
        difficulty: Optional difficulty filter
        doc_type: Optional document type filter
        n_results: Number of results to return

    Returns:
        List of matching documents with metadata
    """
    # Build where clause from non-None filters
    filters = {}

    if category:
        filters["category"] = category
    if problem_type:
        filters["problem_type"] = problem_type
    if difficulty:
        filters["difficulty"] = difficulty
    if doc_type:
        filters["doc_type"] = doc_type

    # Query with or without filters
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where=filters if filters else None,
        include=["documents", "metadatas", "distances"]
    )

    # Format results
    formatted = []
    if results['documents'] and results['documents'][0]:
        for i, doc in enumerate(results['documents'][0]):
            formatted.append({
                'content': doc,
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i],
                'similarity': round((1 - results['distances'][0][i]) * 100, 1)
            })

    return formatted
```

## Bottom Line

Metadata filtering adds user control and precision to your search:

1. **Enrich your metadata** during ingestion with category, problem_type, etc.
2. **Use ChromaDB where clauses** for filtering
3. **Add Streamlit UI** for user-facing filters
4. **Combine with semantic search** for best results

This is especially valuable as your knowledge base grows beyond simple keyword matching.

---

**Next**: [Future Enhancements](07-future-enhancements.md) - Advanced techniques for when you're ready
