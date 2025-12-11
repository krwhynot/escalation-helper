# Escalation Helper - Test Suite

## Setup

First, install test dependencies:

```bash
# Activate virtual environment
source venv/bin/activate

# Install test dependencies
pip install -r requirements-test.txt
```

## Running Tests

### Run all retrieval tests
```bash
pytest tests/test_retrieval.py -v
```

### Run specific test
```bash
pytest tests/test_retrieval.py::test_search_returns_results -v
```

### Run only fast tests (exclude slow integration tests)
```bash
pytest tests/test_retrieval.py -v -m "not slow"
```

### Run with coverage report
```bash
pytest tests/test_retrieval.py --cov=app --cov-report=html
```

## Test Categories

### Basic Functionality
- `test_search_returns_results` - Verifies search returns non-empty results with required fields
- `test_search_respects_limit` - Ensures results don't exceed RETURN_K limit
- `test_search_empty_query` - Tests graceful handling of empty queries
- `test_search_no_results_query` - Tests handling of nonsensical queries

### Void Relevance Tests
- `test_search_relevance_void` - Verifies void queries return void-related content
- `test_search_void_high_confidence` - Ensures void queries have decent confidence scores

### Category-Specific Relevance Tests
- `test_search_relevance_printer` - Tests printer-related queries
- `test_search_relevance_payment` - Tests payment-related queries
- `test_search_relevance_employee` - Tests employee/time clock queries

### Parametrized Category Tests
- `test_search_categories` - Parametrized test covering 7+ different categories:
  - Orders
  - Menu items
  - Cash drawers
  - Delivery
  - Tax calculations
  - Receipts

### Configuration & Quality Tests
- `test_search_respects_distance_threshold` - Verifies distance threshold enforcement
- `test_search_with_reranking` - Tests cross-encoder reranking (if available)
- `test_search_without_reranking` - Tests vector search without reranking
- `test_similarity_percentage_consistency` - Validates similarity scoring math
- `test_results_ordered_by_relevance` - Ensures results are properly ordered

### Integration Tests
- `test_search_common_scenarios` - End-to-end test of common escalation queries

## Prerequisites

Before running tests, ensure:

1. **ChromaDB populated**: Run `python ingest.py` to build the knowledge base
2. **Environment configured**: `.env` file with valid `OPENAI_API_KEY`
3. **Data available**: `data/` directory contains SQL reference documents

## Test Markers

Tests use pytest markers for organization:

- `@pytest.mark.rag` - RAG (Retrieval-Augmented Generation) quality tests
- `@pytest.mark.slow` - Long-running integration tests

Filter tests by marker:
```bash
# Run only RAG tests
pytest -m rag

# Exclude slow tests
pytest -m "not slow"
```

## Expected Test Results

With a properly populated knowledge base:

- **All basic functionality tests** should pass
- **Relevance tests** should pass if knowledge base contains domain-specific content
- **Parametrized tests** may have some failures if certain categories aren't well-represented in the data

## Troubleshooting

### "ChromaDB not found" error
```bash
# Build the database
python ingest.py
```

### "Collection is empty" error
```bash
# Ensure data files exist
ls data/*.md

# Re-run ingestion
python ingest.py
```

### "OpenAI API key" errors
```bash
# Check .env file
cat .env | grep OPENAI_API_KEY

# Ensure key is valid and has credits
```

### Import errors
```bash
# Ensure you're in the venv
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt
```
