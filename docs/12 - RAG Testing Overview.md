# RAG Testing Overview

## Introduction

Testing a Retrieval-Augmented Generation (RAG) system like Escalation Helper requires a fundamentally different approach than traditional software testing. While conventional applications have deterministic outputs that can be validated with simple assertions, RAG systems combine multiple AI components (embeddings, vector search, LLMs) that produce non-deterministic results. This document outlines why specialized testing is critical and how to approach it systematically.

## Why RAG Systems Need Specialized Testing

### Traditional Unit Tests Aren't Enough

In a typical application, you can write tests like:
```python
assert calculate_total(10, 5) == 15
assert format_date("2024-01-15") == "January 15, 2024"
```

But with RAG systems, you can't write:
```python
# This doesn't work for RAG!
assert get_sql_solution("printer won't print") == "UPDATE tblPrinters SET..."
```

The same query might return slightly different wording, different SQL queries, or even different approaches depending on:
- LLM temperature settings
- Model updates
- Retrieved context variations
- Reranking order changes

### Non-Deterministic Outputs from LLMs

Large Language Models are probabilistic by nature. Even with temperature=0 (most deterministic setting), subtle variations occur:
- Different phrasings of the same answer
- Varying levels of detail
- Alternative but equally valid SQL approaches
- Order of presented solutions

**Example:** Query "cashier can't void order" might return:
- Response A: "Check the `tblEmployeePermissions` table for void rights..."
- Response B: "Verify void permissions in employee settings by querying..."

Both are correct, but traditional equality assertions would fail.

### Multiple Components That Can Fail Independently

The Escalation Helper pipeline has several stages:

```
User Query
    ↓
[Embedding] ← Can produce poor vectors
    ↓
[Vector Search] ← Can retrieve wrong documents
    ↓
[Reranking] ← Can reorder incorrectly
    ↓
[Context Assembly] ← Can format poorly
    ↓
[LLM Generation] ← Can hallucinate or ignore context
    ↓
Response
```

A failure at ANY stage breaks the system, but the symptoms might only appear at the end. You need to test each layer independently.

### Quality is Subjective and Context-Dependent

What makes a "good" response?
- **Accuracy**: Contains correct SQL queries
- **Relevance**: Addresses the user's actual problem
- **Completeness**: Includes necessary context and warnings
- **Clarity**: Written at appropriate technical level
- **Safety**: Doesn't suggest destructive operations without warnings

These criteria are subjective and vary by user expertise. A DBA might want raw SQL, while a support agent needs step-by-step instructions.

## The Three Layers to Test

### Layer 1: Retrieval Layer

**Question: Does the system find the right documents?**

This layer tests whether your vector search returns relevant chunks from the knowledge base.

#### What to Test

**Vector Search Quality**
```python
def test_retrieval_finds_printer_docs():
    query = "receipt won't print"
    results = search_knowledge_base(query, k=20)

    # Check that printer-related chunks are in top results
    top_sources = [r['source'] for r in results[:5]]
    assert any('printer' in s.lower() for s in top_sources)
```

**Embedding Accuracy**
- Do similar queries retrieve similar documents?
- Are semantic variations handled? ("can't print" vs "printer broken" vs "receipt not printing")

**Reranking Effectiveness**
```python
def test_reranking_improves_order():
    query = "void transaction permission error"

    # Get results without reranking
    base_results = chromadb_retrieve(query, k=20)

    # Get results with reranking
    reranked = cross_encoder_rerank(base_results)

    # Top result should mention permissions
    assert 'permission' in reranked[0]['content'].lower()
```

#### Key Metrics for Retrieval

- **Recall@k**: Of all relevant documents, how many appear in top k results?
- **Precision@k**: Of top k results, how many are relevant?
- **MRR (Mean Reciprocal Rank)**: Average of 1/rank for first relevant result
- **Average Distance**: Lower distances indicate better semantic matching

**Example Test Case:**
```python
# Golden test case
query = "employee clocked in twice"
expected_topics = ['tblEmployeeTime', 'duplicate punch', 'time clock']

results = search_knowledge_base(query, k=10)
retrieved_text = ' '.join([r['content'] for r in results])

# At least 2 of 3 expected topics should appear
matches = sum(topic in retrieved_text for topic in expected_topics)
assert matches >= 2, f"Only found {matches}/3 expected topics"
```

### Layer 2: Augmentation Layer

**Question: Is the context properly formatted and presented to the LLM?**

This layer tests how you assemble retrieved chunks into a coherent prompt.

#### What to Test

**Chunk Selection**
- Are you including the most relevant chunks?
- Is there redundant information across chunks?
- Are chunks properly deduplicated?

```python
def test_no_duplicate_chunks():
    query = "cash drawer won't open"
    results = search_knowledge_base(query, k=10)

    # Check for exact duplicates
    contents = [r['content'] for r in results]
    assert len(contents) == len(set(contents))
```

**Context Window Management**
- Does the combined context fit within the model's limits?
- Are you truncating in a smart way (removing least relevant first)?

```python
def test_context_fits_in_window():
    query = "explain all payment types"
    context = build_context(query, max_tokens=4000)

    token_count = count_tokens(context)
    assert token_count <= 4000
    assert token_count > 0  # Didn't truncate everything
```

**Prompt Construction**
- Is the system prompt clear and well-structured?
- Are examples formatted consistently?
- Is the user query properly escaped/sanitized?

#### Key Metrics for Augmentation

- **Context Relevance Score**: How relevant is the assembled context to the query?
- **Token Utilization**: Percentage of available context window used
- **Chunk Overlap**: Amount of duplicate information across chunks
- **Source Diversity**: Number of different source documents referenced

### Layer 3: Generation Layer

**Question: Does the LLM produce good responses?**

This layer tests the final output quality.

#### What to Test

**Faithfulness to Context**
```python
def test_no_hallucination():
    query = "reset franchise database"
    context = get_test_context_without_reset_info()

    response = generate_response(query, context)

    # Should not fabricate SQL for something not in context
    assert "I don't have specific information" in response or \
           "not found in documentation" in response
```

**Relevance to Query**
- Does the response actually answer the question?
- Are tangential details minimized?

**Factual Accuracy**
```python
def test_sql_syntax_valid():
    query = "find employee by ID"
    response = generate_response(query, context)

    # Extract SQL from response
    sql_queries = extract_sql_blocks(response)

    for query in sql_queries:
        # Basic syntax validation (doesn't execute)
        assert validate_sql_syntax(query)
```

#### Key Metrics for Generation

- **Faithfulness**: LLM only uses information from provided context
- **Answer Relevance**: Response addresses the user's question
- **BLEU/ROUGE Score**: Similarity to reference answers (for known queries)
- **SQL Validity**: Extracted queries are syntactically correct
- **Safety**: No dangerous operations without explicit warnings

**Example Evaluation:**
```python
def evaluate_response_quality(query, response, context):
    scores = {}

    # 1. Faithfulness: All facts should be in context
    facts = extract_factual_claims(response)
    scores['faithfulness'] = sum(
        fact_in_context(fact, context) for fact in facts
    ) / len(facts)

    # 2. Relevance: Response should match query intent
    scores['relevance'] = compute_semantic_similarity(query, response)

    # 3. SQL Quality: Queries should be valid
    sql_blocks = extract_sql_blocks(response)
    scores['sql_valid'] = all(validate_sql(q) for q in sql_blocks)

    return scores
```

## Common Failure Modes in RAG Systems

Understanding how RAG systems fail helps you design better tests.

### 1. Retrieved Wrong Documents (Retrieval Failure)

**Symptom:** User asks about printers, system retrieves payment documentation.

**Causes:**
- Poor query embedding (question phrased in unexpected way)
- Insufficient training data in knowledge base
- Overly broad or generic queries
- Embedding model doesn't understand domain terminology

**Example:**
```
Query: "Kitchen printer offline"
Retrieved: Credit card processing errors, kitchen menu setup, employee kitchen access
Missing: Printer troubleshooting, network configuration, device drivers
```

**How to Test:**
```python
def test_domain_specific_retrieval():
    # Test that domain terms retrieve correct categories
    test_cases = {
        "bump bar not working": "kitchen",
        "credit card declined": "payment",
        "void permission denied": "employee",
    }

    for query, expected_category in test_cases.items():
        results = search_knowledge_base(query, k=5)
        categories = extract_categories(results)
        assert expected_category in categories[:3]
```

### 2. Retrieved Right Docs But LLM Ignored Them (Generation Failure)

**Symptom:** Correct information is in the context, but the LLM's response doesn't use it.

**Causes:**
- Context buried in middle of long prompt (lost in the middle problem)
- Conflicting information confuses the model
- System prompt not emphasizing faithfulness
- Temperature too high causing creative deviations

**Example:**
```
Context contains: "UPDATE tblPrinters SET IsDefault = 1 WHERE PrinterID = X"
LLM Response: "You'll need to configure the default printer in Windows settings..."
```

**How to Test:**
```python
def test_llm_uses_provided_context():
    # Inject a unique SQL snippet into context
    unique_table = "tblTestXYZ123"
    context = f"To fix this, query {unique_table} table..."

    response = generate_response("How do I fix this?", context)

    # Response should mention the unique table name
    assert unique_table in response
```

### 3. Hallucinated Information Not in Context

**Symptom:** LLM invents plausible-sounding but incorrect SQL queries or table names.

**Causes:**
- Model's pre-training includes generic SQL knowledge
- Insufficient emphasis on context-only responses
- Missing information triggers gap-filling behavior

**Example:**
```
User: "How do I archive old orders?"
Context: [No information about archiving]
LLM: "Use this query: UPDATE tblOrders SET Archived = 1 WHERE OrderDate < '2024-01-01'"
Issue: tblOrders might not have an 'Archived' column
```

**How to Test:**
```python
def test_admits_knowledge_gaps():
    # Query about topic NOT in knowledge base
    query = "How do I configure blockchain integration?"
    context = ""  # Empty context

    response = generate_response(query, context)

    # Should admit lack of information
    uncertainty_phrases = [
        "don't have information",
        "not found in documentation",
        "cannot provide specific",
        "not covered in available"
    ]

    assert any(phrase in response.lower() for phrase in uncertainty_phrases)
```

### 4. Correct Info But Wrong Format for User

**Symptom:** Response is technically accurate but not actionable for the user.

**Causes:**
- Not tailoring response to user expertise level
- Providing SQL without explanation
- Missing step-by-step instructions
- No warnings about potential impacts

**Example:**
```
User: "Why can't cashier access manager functions?"
Bad Response: "SELECT * FROM tblEmployeePermissions WHERE EmployeeID = X"
Good Response: "The cashier likely lacks manager permissions. Here's how to check:
1. Find the employee ID
2. Run this query: SELECT PermissionLevel FROM tblEmployeePermissions WHERE...
3. If PermissionLevel < 5, they don't have manager access
4. To grant access, update with: UPDATE tblEmployeePermissions SET..."
```

**How to Test:**
```python
def test_response_includes_explanation():
    query = "check employee permissions"
    response = generate_response(query, context)

    # Should include both SQL and explanation
    assert has_sql_block(response)
    assert has_explanation_text(response)

    # Explanation should be substantial (not just "Run this query:")
    explanation_length = len(extract_non_sql_text(response))
    assert explanation_length > 50  # At least 50 characters of explanation
```

### 5. Performance/Latency Issues

**Symptom:** System is accurate but too slow for real-time use.

**Causes:**
- Retrieving too many candidates (k too high)
- Reranking all candidates instead of top subset
- Using large LLM when smaller would suffice
- Not caching embeddings or results

**How to Test:**
```python
def test_response_time_acceptable():
    import time

    query = "standard troubleshooting query"
    start = time.time()

    response = get_sql_solution(query)

    elapsed = time.time() - start
    assert elapsed < 3.0  # Must respond in under 3 seconds
```

### 6. Edge Cases

#### Empty Results
```python
def test_handles_no_results():
    # Query that definitely won't match anything
    query = "sdkfjhsdkjfhskdjfh"
    response = get_sql_solution(query)

    # Should handle gracefully, not crash
    assert response is not None
    assert "couldn't find" in response.lower() or "no results" in response.lower()
```

#### Very Long Queries
```python
def test_handles_long_queries():
    # 500-word query
    query = "I have a problem where " + "the system is broken " * 100
    response = get_sql_solution(query)

    # Should still process without error
    assert response is not None
```

#### Ambiguous Queries
```python
def test_asks_for_clarification():
    # Highly ambiguous query
    query = "it's not working"
    response = get_sql_solution(query)

    # Should ask clarifying questions
    assert "?" in response or "clarify" in response.lower()
```

## The RAG Testing Pyramid

Just like the traditional testing pyramid, RAG systems should have many fast tests and fewer slow tests.

```
        /\
       /  \  Human Evaluation (slowest, few)
      /----\
     /      \  End-to-End Tests (slow, some)
    /--------\
   /          \  Integration Tests (medium, more)
  /------------\
 /______________\  Unit Tests (fast, many)
```

### Unit Tests (Fast, Many)

Test individual components in isolation.

**Examples:**
- Embedding generation produces correct shape vectors
- Distance calculations return expected values
- SQL extraction regex works correctly
- Token counting is accurate
- Prompt templates format correctly

```python
def test_extract_sql_blocks():
    text = """
    Here's the solution:
    ```sql
    SELECT * FROM tblOrders
    ```
    And another:
    ```sql
    UPDATE tblPrinters SET IsDefault = 1
    ```
    """

    blocks = extract_sql_blocks(text)
    assert len(blocks) == 2
    assert "SELECT" in blocks[0]
    assert "UPDATE" in blocks[1]
```

**Characteristics:**
- Run in milliseconds
- No external API calls
- Deterministic outputs
- High code coverage

### Integration Tests (Medium, More)

Test how components work together.

**Examples:**
- Embedding + vector search returns reasonable results
- Retrieval + reranking improves order
- Context assembly + LLM produces coherent response
- Follow-up question detection triggers correctly

```python
def test_retrieval_with_reranking():
    query = "payment terminal not responding"

    # Test the integration of search + rerank
    results = search_knowledge_base(query, k=20)  # Uses ChromaDB + cross-encoder

    # Verify results are relevant and well-ordered
    top_result = results[0]
    assert 'payment' in top_result['content'].lower()
    assert top_result['distance'] < 0.3  # High confidence
```

**Characteristics:**
- Run in seconds
- May use test databases or mocked APIs
- Some non-determinism acceptable
- Test realistic scenarios

### End-to-End Tests (Slow, Few)

Test the complete pipeline with real components.

**Examples:**
- User query → final response with real LLM
- Complete session flow with follow-ups
- Performance under realistic load
- Integration with actual knowledge base

```python
def test_complete_troubleshooting_flow():
    # Simulate a real user session
    session = create_test_session()

    # Initial query
    response1 = session.query("printer not working")
    assert has_sql_block(response1)

    # Follow-up
    response2 = session.query("it's a kitchen printer")
    assert 'kitchen' in response2.lower()
    assert has_sql_block(response2)

    # Verify coherence across turns
    assert session.maintains_context()
```

**Characteristics:**
- Run in minutes
- Use real APIs (OpenAI, etc.)
- May cost money per run
- Test critical user journeys

### Human Evaluation (Slowest, Few)

Manual review of system outputs.

**Process:**
1. Collect real user queries
2. Generate responses with current system
3. Have domain experts rate quality (1-5 scale)
4. Track metrics over time

**Evaluation Criteria for Escalation Helper:**
- **Accuracy**: Does the SQL query solve the problem? (1-5)
- **Safety**: Are there appropriate warnings? (Yes/No)
- **Clarity**: Is the explanation understandable? (1-5)
- **Completeness**: Does it cover edge cases? (1-5)

**Example Evaluation Form:**
```markdown
Query: "cashier can't void an order"
Response: [system output]

Accuracy: ⚫⚫⚫⚪⚪ (3/5) - Query is correct but incomplete
Safety: ✓ - Includes warning about permission implications
Clarity: ⚫⚫⚫⚫⚫ (5/5) - Very clear step-by-step
Completeness: ⚫⚫⚫⚪⚪ (3/5) - Missing check for order status

Overall: 3.75/5
Notes: Should also check if order is already settled
```

**Characteristics:**
- Run weekly/monthly
- Expensive (human time)
- Catches subtle quality issues
- Validates automated metrics

## Industry Best Practices

### 1. Separate Retrieval and Generation Testing

Don't test everything at once. Isolate failures by testing each stage:

```python
# Bad: Combined test (hard to debug)
def test_system():
    response = get_sql_solution("printer issue")
    assert "tblPrinters" in response  # Why did this fail?

# Good: Separate tests
def test_retrieval():
    results = search_knowledge_base("printer issue")
    assert any('tblPrinters' in r['content'] for r in results)

def test_generation():
    context = load_test_context_with_printer_info()
    response = generate_response("printer issue", context)
    assert "tblPrinters" in response
```

### 2. Use Golden Datasets with Known-Good Answers

Create a test suite of queries with expected behaviors:

```python
GOLDEN_DATASET = [
    {
        "query": "employee can't clock in",
        "expected_tables": ["tblEmployeeTime", "tblEmployees"],
        "expected_keywords": ["clock", "punch", "time"],
        "should_not_contain": ["payment", "menu"]
    },
    {
        "query": "credit card won't process",
        "expected_tables": ["tblPayments", "tblTenders"],
        "expected_keywords": ["payment", "tender", "credit"],
        "should_not_contain": ["employee", "printer"]
    },
    # Add 50-100 real queries from support tickets
]

def test_golden_dataset():
    for case in GOLDEN_DATASET:
        response = get_sql_solution(case['query'])

        # Check expected content
        for table in case['expected_tables']:
            assert table in response

        # Check no wrong information
        for keyword in case['should_not_contain']:
            assert keyword not in response.lower()
```

### 3. Measure Multiple Metrics, Not Just One

No single metric captures RAG quality. Track a dashboard:

```python
class RAGMetrics:
    def evaluate(self, query, response, context, ground_truth=None):
        return {
            # Retrieval metrics
            'retrieval_recall': self.calculate_recall(query, context),
            'retrieval_precision': self.calculate_precision(query, context),
            'avg_distance': self.average_distance(context),

            # Generation metrics
            'faithfulness': self.check_faithfulness(response, context),
            'answer_relevance': self.semantic_similarity(query, response),
            'sql_validity': self.validate_sql(response),

            # Optional: if ground truth available
            'bleu_score': self.bleu(response, ground_truth) if ground_truth else None,

            # Performance
            'latency_ms': self.measure_latency(),
            'tokens_used': self.count_tokens(response)
        }
```

### 4. Track Metrics Over Time (Regression Testing)

Create a CI/CD pipeline that runs tests on every change:

```yaml
# .github/workflows/rag-tests.yml
name: RAG Quality Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run RAG tests
        run: |
          python -m pytest tests/
          python evaluate_rag.py --dataset golden_queries.json

      - name: Upload metrics
        run: |
          # Store metrics in database/dashboard
          python upload_metrics.py --results test_results.json
```

**Track trends:**
- Is retrieval recall improving or degrading?
- Did the latest prompt change improve faithfulness?
- Are we seeing more hallucinations after model update?

### 5. Test with Real User Queries When Possible

Synthetic tests are good, but real user queries reveal unexpected issues:

**Collecting Real Queries:**
```python
# app.py - Add logging
def get_sql_solution(query: str) -> str:
    # Log every query (anonymized)
    log_query(query, user_id=hash(session_id))

    # ... normal processing ...
    response = generate_response(query, context)

    # Log response quality metrics
    log_metrics(query, response, context)

    return response
```

**Using Logged Data:**
```python
# tests/test_production_queries.py
def test_recent_production_queries():
    # Get last 100 queries from production logs
    recent_queries = load_production_queries(limit=100)

    failures = []
    for query_log in recent_queries:
        try:
            response = get_sql_solution(query_log['query'])

            # Basic quality checks
            if not has_sql_block(response):
                failures.append((query_log['query'], "No SQL found"))
            if len(response) < 50:
                failures.append((query_log['query'], "Response too short"))
        except Exception as e:
            failures.append((query_log['query'], str(e)))

    # Allow some failures, but not too many
    failure_rate = len(failures) / len(recent_queries)
    assert failure_rate < 0.05, f"Too many failures: {failures}"
```

## Practical Testing Strategy for Escalation Helper

Here's a concrete testing approach for this specific system:

### Phase 1: Foundation (Unit Tests)

```python
# tests/test_basic_components.py

def test_document_chunking():
    doc = "A" * 5000  # Long document
    chunks = chunk_document(doc, chunk_size=2000, overlap=200)

    assert all(len(chunk) <= 2000 for chunk in chunks)
    assert len(chunks) > 1
    # Check overlap
    assert chunks[0][-200:] == chunks[1][:200]

def test_sql_extraction():
    response = """
    Try this query:
    ```sql
    SELECT * FROM tblOrders
    WHERE OrderID = 123
    ```
    """

    sql = extract_sql_blocks(response)
    assert len(sql) == 1
    assert "SELECT" in sql[0]
    assert "tblOrders" in sql[0]

def test_category_detection():
    assert detect_category("printer won't print") == "printer"
    assert detect_category("credit card declined") == "payment"
    assert detect_category("employee permission denied") == "employee"
```

### Phase 2: Retrieval Quality (Integration Tests)

```python
# tests/test_retrieval.py

RETRIEVAL_TEST_CASES = [
    ("kitchen printer offline", ["printer", "kitchen", "network"]),
    ("void order permission", ["permission", "void", "employee"]),
    ("cash drawer stuck", ["cash", "drawer", "payment"]),
    ("menu item missing", ["menu", "item", "product"]),
]

def test_retrieval_returns_relevant_docs():
    for query, expected_keywords in RETRIEVAL_TEST_CASES:
        results = search_knowledge_base(query, k=10)

        # At least top 3 should contain expected keywords
        top_3_text = ' '.join([r['content'] for r in results[:3]]).lower()

        matches = sum(kw in top_3_text for kw in expected_keywords)
        assert matches >= 2, f"Query '{query}' only matched {matches}/{len(expected_keywords)} keywords"

def test_reranking_improves_relevance():
    query = "employee timecard duplicate punch"

    # Get initial results
    initial = chromadb_search(query, k=20)

    # Apply reranking
    reranked = cross_encoder_rerank(query, initial)

    # Top result should be more relevant
    # (In this case, should mention employee time specifically)
    assert 'employee' in reranked[0]['content'].lower()
    assert 'time' in reranked[0]['content'].lower()
```

### Phase 3: End-to-End Quality (E2E Tests)

```python
# tests/test_e2e.py

@pytest.mark.slow  # These tests call OpenAI
@pytest.mark.requires_api
def test_sql_troubleshooting_flow():
    test_cases = [
        {
            "query": "cashier can't void an order",
            "expected_tables": ["tblEmployeePermissions", "tblOrders"],
            "expected_explanation": True,
            "should_warn": True  # Should warn about permission implications
        },
        {
            "query": "kitchen printer not printing tickets",
            "expected_tables": ["tblPrinters", "tblPrintJobs"],
            "expected_explanation": True,
            "should_warn": False
        }
    ]

    for case in test_cases:
        response = get_sql_solution(case['query'])

        # Check SQL tables mentioned
        for table in case['expected_tables']:
            assert table in response, f"Missing expected table {table}"

        # Check has explanation (not just SQL)
        if case['expected_explanation']:
            non_sql = extract_non_sql_text(response)
            assert len(non_sql) > 100, "Insufficient explanation"

        # Check warnings
        if case['should_warn']:
            warnings = ['warning', 'caution', 'careful', 'important']
            assert any(w in response.lower() for w in warnings)

def test_followup_question_flow():
    # Test the clarification system
    response1 = get_sql_solution("it's not working")

    # Should detect low confidence and ask questions
    assert "?" in response1 or "more information" in response1.lower()
```

### Phase 4: Production Monitoring

```python
# monitoring/rag_metrics.py

class RAGMonitoring:
    def log_query(self, query, response, context, metrics):
        """Log every production query with metrics"""
        log_entry = {
            'timestamp': datetime.now(),
            'query': query,
            'response_length': len(response),
            'num_sql_blocks': len(extract_sql_blocks(response)),
            'retrieval_distance': metrics['avg_distance'],
            'processing_time_ms': metrics['latency'],
            'context_size': len(context),
        }

        # Store in database or metrics service
        self.db.insert('query_logs', log_entry)

    def daily_quality_report(self):
        """Generate daily quality metrics"""
        today_queries = self.db.get_recent_queries(hours=24)

        report = {
            'total_queries': len(today_queries),
            'avg_confidence': np.mean([q['retrieval_distance'] for q in today_queries]),
            'queries_with_sql': sum(1 for q in today_queries if q['num_sql_blocks'] > 0),
            'avg_response_time': np.mean([q['processing_time_ms'] for q in today_queries]),
            'slow_queries': [q for q in today_queries if q['processing_time_ms'] > 5000]
        }

        # Alert if quality degrades
        if report['avg_confidence'] > 0.35:
            self.alert("High average distance - retrieval quality degraded")

        return report
```

## Conclusion

Testing RAG systems requires a multi-layered approach:

1. **Unit tests** ensure individual components work correctly
2. **Integration tests** verify components work together
3. **End-to-end tests** validate the full pipeline with real models
4. **Human evaluation** catches subtle quality issues
5. **Production monitoring** tracks real-world performance

For Escalation Helper specifically, focus on:
- Testing retrieval quality with domain-specific SQL queries
- Validating that responses include both SQL and explanations
- Ensuring safety warnings appear for destructive operations
- Monitoring production queries to catch edge cases

Remember: RAG testing is an ongoing process, not a one-time task. Continuously refine your test suite based on real user interactions and failure modes you discover.
