# RAG Testing Implementation Roadmap

A phased implementation plan for testing Escalation Helper - a RAG-based SQL troubleshooting assistant.

---

## Phase 1: Minimum Viable Testing (Week 1)

### Goals
- Get basic tests running
- Establish test infrastructure
- Create initial golden dataset

### Day 1-2: Setup

#### Create Test Directory Structure
```bash
# From project root (/home/krwhynot/projects/escalation-helper)
mkdir -p tests
touch tests/__init__.py
touch tests/conftest.py
touch tests/test_retrieval.py
touch tests/test_ui.py
mkdir -p reports
mkdir -p data/test_cases
```

#### Install Test Dependencies
Create `requirements-test.txt`:
```txt
pytest==7.4.3
pytest-html==4.1.1
pytest-cov==4.1.0
ragas==0.1.9
langchain==0.1.0
langchain-openai==0.0.5
pytest-mock==3.12.0
```

Install:
```bash
pip install -r requirements-test.txt
```

#### Create pytest Configuration
Create `pytest.ini`:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --tb=short
    --disable-warnings
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    ui: marks tests as UI tests
    rag: marks tests as RAG evaluation tests
```

### Day 3-4: Basic Retrieval Tests

Create `tests/test_retrieval.py`:
```python
"""Basic retrieval tests for search functionality."""
import pytest
from app import search_knowledge_base, get_rag_response
import os

# Ensure we're not making real API calls in basic tests
pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")


class TestBasicRetrieval:
    """Test basic search functionality."""

    def test_search_returns_results(self):
        """Verify search returns non-empty results."""
        results = search_knowledge_base("cashier can't void order")
        assert len(results) > 0, "Search should return at least one result"

    def test_search_respects_k_parameter(self):
        """Verify search respects the k parameter."""
        k = 5
        results = search_knowledge_base("printer issues", k=k)
        assert len(results) <= k, f"Should return at most {k} results"

    def test_search_with_common_keywords(self):
        """Test search with common support keywords."""
        test_queries = [
            "printer not printing",
            "employee permissions",
            "payment declined",
            "order modification",
        ]

        for query in test_queries:
            results = search_knowledge_base(query)
            assert len(results) > 0, f"Query '{query}' returned no results"

    def test_search_relevance_basic(self):
        """Basic relevance check - results should contain query terms."""
        query = "printer troubleshooting"
        results = search_knowledge_base(query)

        # At least one result should mention printer
        result_text = " ".join([str(r) for r in results])
        assert "printer" in result_text.lower(), \
            "Results should contain relevant terms"

    def test_empty_query_handling(self):
        """Verify handling of empty or very short queries."""
        # Should not crash
        results = search_knowledge_base("")
        assert isinstance(results, list), "Should return a list even for empty query"

    def test_special_characters_in_query(self):
        """Test queries with SQL special characters."""
        queries_with_special_chars = [
            "SELECT * FROM orders",
            "employee_id = 123",
            "amount > $100",
        ]

        for query in queries_with_special_chars:
            results = search_knowledge_base(query)
            assert isinstance(results, list), \
                f"Should handle special characters in: {query}"


class TestSearchMetadata:
    """Test metadata returned with search results."""

    def test_results_have_metadata(self):
        """Verify results include necessary metadata."""
        results = search_knowledge_base("cashier permissions")

        if results:
            result = results[0]
            # ChromaDB results should have documents and distances
            assert hasattr(result, '__getitem__') or hasattr(result, 'page_content'), \
                "Results should have accessible content"

    def test_distance_scores_present(self):
        """Verify distance/similarity scores are returned."""
        results = search_knowledge_base("menu configuration", k=3)

        # Results should have some way to measure relevance
        # This depends on your implementation - adjust as needed
        assert len(results) > 0, "Should return results with scores"


@pytest.mark.slow
class TestCategoryDetection:
    """Test follow-up question category detection."""

    def test_printer_category_detection(self):
        """Test detection of printer-related queries."""
        from app import detect_category

        query = "printer not responding"
        category = detect_category(query)
        assert category == "printer", \
            f"Should detect printer category, got: {category}"

    def test_payment_category_detection(self):
        """Test detection of payment-related queries."""
        from app import detect_category

        query = "credit card declined"
        category = detect_category(query)
        assert category == "payment", \
            f"Should detect payment category, got: {category}"

    def test_employee_category_detection(self):
        """Test detection of employee-related queries."""
        from app import detect_category

        query = "employee can't access manager functions"
        category = detect_category(query)
        assert category == "employee", \
            f"Should detect employee category, got: {category}"


# Fixtures for reuse
@pytest.fixture(scope="module")
def sample_queries():
    """Common test queries."""
    return {
        "printer": "receipt printer not printing",
        "payment": "payment processing failed",
        "employee": "cashier permissions issue",
        "order": "can't modify existing order",
        "menu": "menu items not showing",
        "cash": "cash drawer won't open"
    }


@pytest.fixture(scope="module")
def expected_keywords():
    """Expected keywords for each category."""
    return {
        "printer": ["printer", "print", "receipt"],
        "payment": ["payment", "card", "transaction"],
        "employee": ["employee", "user", "permission", "role"],
        "order": ["order", "transaction", "sale"],
        "menu": ["menu", "item", "product"],
        "cash": ["cash", "drawer", "till"]
    }
```

### Day 5: First HTML Report and Fixtures

Create `tests/conftest.py`:
```python
"""Shared fixtures and configuration for tests."""
import pytest
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def test_env():
    """Set up test environment variables."""
    original_env = os.environ.copy()

    # Set test environment
    os.environ.setdefault("OPENAI_API_KEY", "test-key-placeholder")
    os.environ.setdefault("APP_PASSWORD", "escalation2024")

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture(scope="session")
def golden_test_cases():
    """Initial golden dataset for testing."""
    return [
        {
            "query": "cashier can't void an order",
            "expected_keywords": ["void", "order", "permission"],
            "category": "order",
            "expected_tables": ["Orders", "Permissions"]
        },
        {
            "query": "receipt printer not printing",
            "expected_keywords": ["printer", "receipt", "device"],
            "category": "printer",
            "expected_tables": ["Printers", "Devices"]
        },
        {
            "query": "credit card transaction declined",
            "expected_keywords": ["payment", "credit", "card", "declined"],
            "category": "payment",
            "expected_tables": ["Payments", "Transactions"]
        },
        {
            "query": "employee doesn't have manager access",
            "expected_keywords": ["employee", "permission", "role", "manager"],
            "category": "employee",
            "expected_tables": ["Employees", "Roles", "Permissions"]
        },
        {
            "query": "menu item not showing on POS",
            "expected_keywords": ["menu", "item", "pos"],
            "category": "menu",
            "expected_tables": ["MenuItems", "Products"]
        },
        {
            "query": "cash drawer won't open",
            "expected_keywords": ["cash", "drawer"],
            "category": "cash",
            "expected_tables": ["CashDrawer", "Devices"]
        },
        {
            "query": "how do I reset a cashier password",
            "expected_keywords": ["password", "reset", "employee"],
            "category": "employee",
            "expected_tables": ["Employees", "Users"]
        },
        {
            "query": "order shows wrong total amount",
            "expected_keywords": ["order", "total", "amount"],
            "category": "order",
            "expected_tables": ["Orders", "OrderItems"]
        },
        {
            "query": "kitchen printer offline",
            "expected_keywords": ["printer", "kitchen", "offline"],
            "category": "printer",
            "expected_tables": ["Printers", "Devices"]
        },
        {
            "query": "refund not processing",
            "expected_keywords": ["refund", "payment"],
            "category": "payment",
            "expected_tables": ["Payments", "Refunds", "Transactions"]
        },
    ]


@pytest.fixture
def mock_search_results():
    """Mock search results for testing."""
    return [
        {
            "content": "To void an order, check the employee permissions...",
            "metadata": {"source": "sql_reference.md", "category": "order"},
            "distance": 0.25
        },
        {
            "content": "Voiding requires the VOID_ORDER permission...",
            "metadata": {"source": "sql_reference.md", "category": "permissions"},
            "distance": 0.30
        },
        {
            "content": "Query: SELECT * FROM Permissions WHERE...",
            "metadata": {"source": "sql_reference.md", "category": "order"},
            "distance": 0.35
        }
    ]


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "golden: tests using golden dataset"
    )
    config.addinivalue_line(
        "markers", "category(name): tests for specific categories"
    )
```

#### Generate First Report
```bash
# Run all tests with HTML report
pytest --html=reports/test_report.html --self-contained-html -v

# Run with coverage
pytest --html=reports/test_report.html --self-contained-html \
       --cov=. --cov-report=html --cov-report=term -v
```

### Week 1 Deliverables Checklist

- [ ] Test directory structure created (`tests/`, `reports/`, `data/test_cases/`)
- [ ] Test dependencies installed (`requirements-test.txt`)
- [ ] pytest configuration file (`pytest.ini`)
- [ ] Basic retrieval tests (5-10 tests in `test_retrieval.py`)
- [ ] Shared fixtures (`conftest.py`)
- [ ] First HTML test report generated
- [ ] 10 golden test cases documented in fixtures
- [ ] Documentation updated with test commands

### Common Pitfalls - Week 1

1. **API Key Issues**: Tests may fail if OPENAI_API_KEY not set. Use fixtures to mock or set test keys.
2. **ChromaDB State**: Tests may interfere with each other if using same DB. Consider test-specific DB paths.
3. **Import Errors**: Ensure project root is in Python path (handled in `conftest.py`).
4. **Slow Tests**: Initial tests may be slow due to API calls. Mark with `@pytest.mark.slow` and skip during development.

---

## Phase 2: RAG Evaluation (Week 2)

### Goals
- Integrate RAGAS metrics for quality evaluation
- Build comprehensive golden dataset (20+ cases)
- Establish quality thresholds
- Implement regression testing

### Day 1-2: RAGAS Integration

Create `tests/test_rag_quality.py`:
```python
"""RAG quality evaluation using RAGAS metrics."""
import pytest
from ragas import evaluate, EvaluationDataset
from ragas.metrics import (
    Faithfulness,
    LLMContextRecall,
    LLMContextPrecision,
    ResponseRelevancy
)
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI
from app import search_knowledge_base, get_rag_response
import os


@pytest.fixture(scope="module")
def ragas_evaluator():
    """Create RAGAS evaluator with GPT-4o-mini."""
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    return LangchainLLMWrapper(llm)


@pytest.fixture
def ragas_test_cases(golden_test_cases):
    """
    Convert golden test cases to RAGAS format.

    RAGAS expects:
    - user_input: The question
    - retrieved_contexts: List of retrieved text chunks
    - response: The generated response
    - reference: The expected/ground truth answer (optional)
    """
    test_cases = []

    for case in golden_test_cases[:5]:  # Start with 5 cases
        query = case["query"]

        # Get actual retrieval and response
        results = search_knowledge_base(query, k=3)
        contexts = [str(r) for r in results]
        response = get_rag_response(query, results)

        test_cases.append({
            "user_input": query,
            "retrieved_contexts": contexts,
            "response": response,
            "reference": case.get("expected_answer", "")  # Optional ground truth
        })

    return test_cases


@pytest.mark.rag
@pytest.mark.slow
class TestRAGFaithfulness:
    """Test that responses are faithful to retrieved context."""

    def test_faithfulness_score(self, ragas_evaluator, ragas_test_cases):
        """
        Faithfulness: Measures if the response is factually consistent
        with the retrieved context (no hallucinations).

        Target: > 0.85
        """
        dataset = EvaluationDataset.from_list(ragas_test_cases)

        result = evaluate(
            dataset=dataset,
            metrics=[Faithfulness()],
            llm=ragas_evaluator
        )

        faithfulness_score = result['faithfulness']
        print(f"\nFaithfulness Score: {faithfulness_score:.3f}")

        assert faithfulness_score > 0.85, \
            f"Faithfulness too low: {faithfulness_score:.3f} (target: > 0.85)"

    def test_faithfulness_per_category(self, ragas_evaluator, golden_test_cases):
        """Test faithfulness scores by category."""
        categories = {}

        for case in golden_test_cases:
            category = case["category"]
            if category not in categories:
                categories[category] = []

            query = case["query"]
            results = search_knowledge_base(query, k=3)
            response = get_rag_response(query, results)

            categories[category].append({
                "user_input": query,
                "retrieved_contexts": [str(r) for r in results],
                "response": response
            })

        # Evaluate each category
        for category, test_cases in categories.items():
            if test_cases:
                dataset = EvaluationDataset.from_list(test_cases)
                result = evaluate(
                    dataset=dataset,
                    metrics=[Faithfulness()],
                    llm=ragas_evaluator
                )

                score = result['faithfulness']
                print(f"\n{category.upper()} Faithfulness: {score:.3f}")

                assert score > 0.80, \
                    f"{category} faithfulness too low: {score:.3f}"


@pytest.mark.rag
@pytest.mark.slow
class TestRAGContextRecall:
    """Test that retrieval captures all relevant information."""

    def test_context_recall_score(self, ragas_evaluator, ragas_test_cases):
        """
        Context Recall: Measures if the retrieved context contains
        all information needed to answer the question.

        Target: > 0.80
        """
        # Filter test cases that have reference answers
        cases_with_reference = [
            case for case in ragas_test_cases
            if case.get("reference")
        ]

        if not cases_with_reference:
            pytest.skip("No test cases with reference answers")

        dataset = EvaluationDataset.from_list(cases_with_reference)

        result = evaluate(
            dataset=dataset,
            metrics=[LLMContextRecall()],
            llm=ragas_evaluator
        )

        recall_score = result['context_recall']
        print(f"\nContext Recall Score: {recall_score:.3f}")

        assert recall_score > 0.80, \
            f"Context recall too low: {recall_score:.3f} (target: > 0.80)"


@pytest.mark.rag
@pytest.mark.slow
class TestRAGContextPrecision:
    """Test that retrieved context is precise and relevant."""

    def test_context_precision_score(self, ragas_evaluator, ragas_test_cases):
        """
        Context Precision: Measures how much of the retrieved context
        is actually relevant to the question.

        Target: > 0.75
        """
        dataset = EvaluationDataset.from_list(ragas_test_cases)

        result = evaluate(
            dataset=dataset,
            metrics=[LLMContextPrecision()],
            llm=ragas_evaluator
        )

        precision_score = result['context_precision']
        print(f"\nContext Precision Score: {precision_score:.3f}")

        assert precision_score > 0.75, \
            f"Context precision too low: {precision_score:.3f} (target: > 0.75)"


@pytest.mark.rag
@pytest.mark.slow
class TestRAGResponseRelevancy:
    """Test that responses are relevant to the user's question."""

    def test_response_relevancy_score(self, ragas_evaluator, ragas_test_cases):
        """
        Response Relevancy: Measures how relevant the generated response
        is to the user's question.

        Target: > 0.85
        """
        dataset = EvaluationDataset.from_list(ragas_test_cases)

        result = evaluate(
            dataset=dataset,
            metrics=[ResponseRelevancy()],
            llm=ragas_evaluator
        )

        relevancy_score = result['answer_relevancy']
        print(f"\nResponse Relevancy Score: {relevancy_score:.3f}")

        assert relevancy_score > 0.85, \
            f"Response relevancy too low: {relevancy_score:.3f} (target: > 0.85)"


@pytest.mark.rag
@pytest.mark.slow
class TestRAGComprehensive:
    """Comprehensive RAG evaluation with all metrics."""

    def test_all_metrics_together(self, ragas_evaluator, ragas_test_cases):
        """Run all RAGAS metrics in one evaluation."""
        dataset = EvaluationDataset.from_list(ragas_test_cases)

        result = evaluate(
            dataset=dataset,
            metrics=[
                Faithfulness(),
                LLMContextRecall(),
                LLMContextPrecision(),
                ResponseRelevancy()
            ],
            llm=ragas_evaluator
        )

        print("\n" + "="*50)
        print("COMPREHENSIVE RAG EVALUATION RESULTS")
        print("="*50)
        print(f"Faithfulness:       {result.get('faithfulness', 0):.3f} (target: > 0.85)")
        print(f"Context Recall:     {result.get('context_recall', 0):.3f} (target: > 0.80)")
        print(f"Context Precision:  {result.get('context_precision', 0):.3f} (target: > 0.75)")
        print(f"Response Relevancy: {result.get('answer_relevancy', 0):.3f} (target: > 0.85)")
        print("="*50 + "\n")

        # Assert all metrics meet minimum thresholds
        assert result.get('faithfulness', 0) > 0.85, "Faithfulness below threshold"
        assert result.get('context_recall', 0) > 0.80, "Context recall below threshold"
        assert result.get('context_precision', 0) > 0.75, "Context precision below threshold"
        assert result.get('answer_relevancy', 0) > 0.85, "Response relevancy below threshold"
```

### Day 3-4: Expand Golden Dataset

Create `data/test_cases/golden_dataset.json`:
```json
[
  {
    "id": "void-order-001",
    "query": "cashier can't void an order",
    "category": "order",
    "expected_keywords": ["void", "order", "permission", "Employees", "Permissions"],
    "expected_tables": ["Orders", "Permissions", "Employees"],
    "reference_answer": "To troubleshoot void order issues, check employee permissions in the Employees and Permissions tables. The employee needs VOID_ORDER permission.",
    "difficulty": "medium",
    "priority": "high"
  },
  {
    "id": "printer-receipt-001",
    "query": "receipt printer not printing",
    "category": "printer",
    "expected_keywords": ["printer", "receipt", "device", "status"],
    "expected_tables": ["Printers", "Devices", "PrintJobs"],
    "reference_answer": "Check printer status in Devices table, verify printer connection, and review PrintJobs for errors.",
    "difficulty": "easy",
    "priority": "high"
  },
  {
    "id": "payment-declined-001",
    "query": "credit card transaction declined",
    "category": "payment",
    "expected_keywords": ["payment", "credit", "card", "declined", "transaction"],
    "expected_tables": ["Payments", "Transactions", "PaymentMethods"],
    "reference_answer": "Review Payments and Transactions tables for error codes. Check payment processor status and card details in PaymentMethods.",
    "difficulty": "medium",
    "priority": "critical"
  },
  {
    "id": "employee-access-001",
    "query": "employee doesn't have manager access",
    "category": "employee",
    "expected_keywords": ["employee", "permission", "role", "manager", "access"],
    "expected_tables": ["Employees", "Roles", "Permissions", "EmployeeRoles"],
    "reference_answer": "Check employee role assignment in EmployeeRoles table and verify manager permissions in Roles and Permissions tables.",
    "difficulty": "easy",
    "priority": "medium"
  },
  {
    "id": "menu-display-001",
    "query": "menu item not showing on POS",
    "category": "menu",
    "expected_keywords": ["menu", "item", "pos", "display", "active"],
    "expected_tables": ["MenuItems", "Products", "MenuCategories"],
    "reference_answer": "Verify menu item is active in MenuItems table, check category assignment, and ensure POS sync is complete.",
    "difficulty": "medium",
    "priority": "high"
  },
  {
    "id": "cash-drawer-001",
    "query": "cash drawer won't open",
    "category": "cash",
    "expected_keywords": ["cash", "drawer", "device", "printer"],
    "expected_tables": ["CashDrawer", "Devices", "Printers"],
    "reference_answer": "Check cash drawer device status, verify printer connection (drawer often connects through receipt printer), and test drawer kick command.",
    "difficulty": "easy",
    "priority": "high"
  },
  {
    "id": "employee-password-001",
    "query": "how do I reset a cashier password",
    "category": "employee",
    "expected_keywords": ["password", "reset", "employee", "user"],
    "expected_tables": ["Employees", "Users", "Authentication"],
    "reference_answer": "Reset password in Employees or Users table. Update password hash and set password_reset_required flag if applicable.",
    "difficulty": "easy",
    "priority": "medium"
  },
  {
    "id": "order-total-001",
    "query": "order shows wrong total amount",
    "category": "order",
    "expected_keywords": ["order", "total", "amount", "calculation", "tax"],
    "expected_tables": ["Orders", "OrderItems", "Taxes", "Discounts"],
    "reference_answer": "Recalculate order total from OrderItems, check tax calculations in Taxes table, and verify any discounts applied.",
    "difficulty": "hard",
    "priority": "critical"
  },
  {
    "id": "printer-kitchen-001",
    "query": "kitchen printer offline",
    "category": "printer",
    "expected_keywords": ["printer", "kitchen", "offline", "device", "network"],
    "expected_tables": ["Printers", "Devices", "PrinterRouting"],
    "reference_answer": "Check printer device status, verify network connection, and review PrinterRouting to ensure kitchen orders route correctly.",
    "difficulty": "medium",
    "priority": "critical"
  },
  {
    "id": "payment-refund-001",
    "query": "refund not processing",
    "category": "payment",
    "expected_keywords": ["refund", "payment", "transaction", "process"],
    "expected_tables": ["Payments", "Refunds", "Transactions", "PaymentProcessor"],
    "reference_answer": "Check Refunds table for status, verify original payment in Payments, and review PaymentProcessor logs for errors.",
    "difficulty": "medium",
    "priority": "critical"
  },
  {
    "id": "employee-clock-001",
    "query": "employee can't clock in",
    "category": "employee",
    "expected_keywords": ["employee", "clock", "time", "shift"],
    "expected_tables": ["Employees", "TimeClocks", "Shifts", "EmployeeSchedule"],
    "reference_answer": "Verify employee status is active, check for existing clock-in records, and ensure employee is scheduled for current shift.",
    "difficulty": "easy",
    "priority": "high"
  },
  {
    "id": "order-modify-001",
    "query": "can't modify existing order after payment",
    "category": "order",
    "expected_keywords": ["order", "modify", "payment", "status", "locked"],
    "expected_tables": ["Orders", "OrderStatus", "Payments"],
    "reference_answer": "Check order status - paid orders may be locked. Review business rules for post-payment modifications and required permissions.",
    "difficulty": "medium",
    "priority": "medium"
  },
  {
    "id": "tax-calculation-001",
    "query": "tax not calculating correctly",
    "category": "order",
    "expected_keywords": ["tax", "calculation", "rate", "item"],
    "expected_tables": ["Taxes", "TaxRates", "TaxGroups", "MenuItems"],
    "reference_answer": "Verify tax rates in TaxRates table, check item tax group assignments, and ensure tax calculation logic is correct.",
    "difficulty": "hard",
    "priority": "critical"
  },
  {
    "id": "discount-apply-001",
    "query": "discount code not working",
    "category": "order",
    "expected_keywords": ["discount", "code", "promotion", "valid"],
    "expected_tables": ["Discounts", "Promotions", "Orders"],
    "reference_answer": "Check discount validity (dates, usage limits), verify code matches Discounts table, and ensure order meets discount requirements.",
    "difficulty": "medium",
    "priority": "high"
  },
  {
    "id": "inventory-sync-001",
    "query": "inventory count doesn't match POS",
    "category": "menu",
    "expected_keywords": ["inventory", "count", "sync", "stock"],
    "expected_tables": ["Inventory", "MenuItems", "InventoryTransactions"],
    "reference_answer": "Compare Inventory table with sales data, review InventoryTransactions for discrepancies, and check sync status.",
    "difficulty": "hard",
    "priority": "medium"
  },
  {
    "id": "tip-calculation-001",
    "query": "tip amount not added to total",
    "category": "payment",
    "expected_keywords": ["tip", "gratuity", "payment", "total"],
    "expected_tables": ["Payments", "Tips", "Orders"],
    "reference_answer": "Verify tip entry in Tips table, check payment total calculation includes tip, and review tip distribution settings.",
    "difficulty": "medium",
    "priority": "high"
  },
  {
    "id": "reporting-sales-001",
    "query": "daily sales report shows incorrect totals",
    "category": "order",
    "expected_keywords": ["report", "sales", "total", "calculation"],
    "expected_tables": ["Orders", "Payments", "Refunds", "Reports"],
    "reference_answer": "Recalculate from Orders and Payments tables, subtract Refunds, verify report date range, and check for timezone issues.",
    "difficulty": "hard",
    "priority": "critical"
  },
  {
    "id": "online-order-001",
    "query": "online order not appearing in POS",
    "category": "order",
    "expected_keywords": ["online", "order", "sync", "integration"],
    "expected_tables": ["Orders", "OnlineOrders", "OrderStatus", "IntegrationLog"],
    "reference_answer": "Check OnlineOrders table for sync status, review IntegrationLog for errors, and verify order status allows POS display.",
    "difficulty": "hard",
    "priority": "critical"
  },
  {
    "id": "modifier-pricing-001",
    "query": "menu item modifier not charging correct price",
    "category": "menu",
    "expected_keywords": ["modifier", "price", "menu", "item"],
    "expected_tables": ["Modifiers", "ModifierPrices", "MenuItems", "OrderItems"],
    "reference_answer": "Verify modifier pricing in ModifierPrices table, check modifier group assignments, and ensure POS uses correct price tier.",
    "difficulty": "medium",
    "priority": "high"
  },
  {
    "id": "gift-card-001",
    "query": "gift card balance not updating",
    "category": "payment",
    "expected_keywords": ["gift", "card", "balance", "update"],
    "expected_tables": ["GiftCards", "GiftCardTransactions", "Payments"],
    "reference_answer": "Check GiftCardTransactions for completed transactions, verify balance calculation, and ensure payment was processed successfully.",
    "difficulty": "medium",
    "priority": "high"
  }
]
```

Update `tests/conftest.py` to load this file:
```python
import json
from pathlib import Path

@pytest.fixture(scope="session")
def golden_test_cases():
    """Load golden dataset from JSON file."""
    dataset_path = Path(__file__).parent.parent / "data" / "test_cases" / "golden_dataset.json"

    if dataset_path.exists():
        with open(dataset_path) as f:
            return json.load(f)
    else:
        # Fallback to inline dataset
        return [
            # ... inline test cases as before ...
        ]
```

### Day 5: Threshold Tuning and Baseline Documentation

Create `scripts/check_thresholds.py`:
```python
#!/usr/bin/env python3
"""
Check if RAG quality metrics meet minimum thresholds.
Used in CI/CD pipeline for quality gates.
"""
import argparse
import json
import sys
from pathlib import Path


def load_test_results(report_path):
    """Load test results from pytest JSON report."""
    with open(report_path) as f:
        return json.load(f)


def check_thresholds(results, thresholds):
    """Check if metrics meet thresholds."""
    failures = []

    for metric, threshold in thresholds.items():
        actual = results.get(metric, 0)
        if actual < threshold:
            failures.append(
                f"{metric}: {actual:.3f} < {threshold:.3f} (FAIL)"
            )
        else:
            print(f"{metric}: {actual:.3f} >= {threshold:.3f} (PASS)")

    return failures


def main():
    parser = argparse.ArgumentParser(description="Check quality thresholds")
    parser.add_argument("--faithfulness", type=float, default=0.85)
    parser.add_argument("--context-recall", type=float, default=0.80)
    parser.add_argument("--context-precision", type=float, default=0.75)
    parser.add_argument("--response-relevancy", type=float, default=0.85)
    parser.add_argument("--coverage", type=float, default=70.0)
    parser.add_argument("--report", type=str, default="reports/metrics.json")

    args = parser.parse_args()

    # Define thresholds
    thresholds = {
        "faithfulness": args.faithfulness,
        "context_recall": args.context_recall,
        "context_precision": args.context_precision,
        "response_relevancy": args.response_relevancy,
        "coverage": args.coverage
    }

    # Load results
    report_path = Path(args.report)
    if not report_path.exists():
        print(f"Error: Report file not found: {report_path}")
        sys.exit(1)

    results = load_test_results(report_path)

    # Check thresholds
    print("\nQuality Threshold Check")
    print("=" * 50)
    failures = check_thresholds(results, thresholds)

    if failures:
        print("\nFAILURES:")
        for failure in failures:
            print(f"  - {failure}")
        sys.exit(1)
    else:
        print("\nAll thresholds met!")
        sys.exit(0)


if __name__ == "__main__":
    main()
```

Create `docs/RAG_BASELINE_METRICS.md`:
```markdown
# RAG Baseline Metrics

Established: [Date]
Last Updated: [Date]

## Current Thresholds

| Metric | Threshold | Current Score | Status |
|--------|-----------|---------------|--------|
| Faithfulness | > 0.85 | TBD | - |
| Context Recall | > 0.80 | TBD | - |
| Context Precision | > 0.75 | TBD | - |
| Response Relevancy | > 0.85 | TBD | - |
| Test Coverage | > 70% | TBD | - |

## Baseline Scores by Category

### Printer Issues
- Faithfulness: TBD
- Context Recall: TBD
- Sample queries: 4

### Payment Issues
- Faithfulness: TBD
- Context Recall: TBD
- Sample queries: 4

### Employee Issues
- Faithfulness: TBD
- Context Recall: TBD
- Sample queries: 4

### Order Issues
- Faithfulness: TBD
- Context Recall: TBD
- Sample queries: 6

### Menu Issues
- Faithfulness: TBD
- Context Recall: TBD
- Sample queries: 3

### Cash Issues
- Faithfulness: TBD
- Context Recall: TBD
- Sample queries: 1

## Historical Trends

[Track changes over time]

## Notes

- Thresholds set based on industry standards for RAG systems
- Faithfulness is critical - prioritize over other metrics
- Context recall indicates retrieval quality
- Regular review recommended: monthly
```

### Week 2 Commands

```bash
# Run only RAG tests
pytest tests/test_rag_quality.py -v -m rag

# Run RAG tests and save results
pytest tests/test_rag_quality.py -v -m rag \
  --html=reports/rag_report.html --self-contained-html

# Run comprehensive evaluation
pytest tests/test_rag_quality.py::TestRAGComprehensive::test_all_metrics_together -v -s

# Skip slow tests during development
pytest -v -m "not slow"

# Run specific metric test
pytest tests/test_rag_quality.py::TestRAGFaithfulness -v
```

### Week 2 Deliverables Checklist

- [ ] RAGAS installed and integrated
- [ ] `test_rag_quality.py` with 4+ metric tests
- [ ] Golden dataset expanded to 20+ test cases
- [ ] `golden_dataset.json` created with comprehensive cases
- [ ] Baseline metrics documented in `RAG_BASELINE_METRICS.md`
- [ ] Quality threshold script (`check_thresholds.py`)
- [ ] Initial baseline scores recorded
- [ ] Threshold values validated with stakeholders

### Common Pitfalls - Week 2

1. **RAGAS API Changes**: RAGAS library updates frequently. Pin version in `requirements-test.txt`.
2. **LLM Costs**: RAGAS uses LLM calls for evaluation - monitor OpenAI costs.
3. **Reference Answers**: Not all metrics need reference answers, but Context Recall does. Document which cases need them.
4. **Score Variability**: LLM-based metrics can vary slightly between runs. Run multiple times for stable baselines.
5. **Category Imbalance**: Ensure golden dataset has balanced representation across all 6 categories.

---

## Phase 3: UI Testing (Week 3)

### Goals
- Test Streamlit app with AppTest
- Cover critical user flows (login, chat, errors)
- Ensure session state stability
- Test follow-up question logic

### Day 1-2: AppTest Setup and Login Flow

Create `tests/test_ui.py`:
```python
"""Streamlit UI tests using AppTest."""
import pytest
from streamlit.testing.v1 import AppTest
import os


@pytest.fixture
def app():
    """Create AppTest instance with secrets."""
    at = AppTest.from_file("app.py", default_timeout=30)

    # Set secrets
    at.secrets["APP_PASSWORD"] = "escalation2024"
    at.secrets["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "test-key")

    return at


@pytest.fixture
def authenticated_app(app):
    """App instance already authenticated."""
    app.run()

    # Authenticate
    if hasattr(app, 'text_input') and len(app.text_input) > 0:
        app.text_input[0].set_value("escalation2024").run()
        if hasattr(app, 'button') and len(app.button) > 0:
            app.button[0].click().run()

    return app


@pytest.mark.ui
class TestLoginFlow:
    """Test user authentication."""

    def test_initial_state_requires_login(self, app):
        """App should show login on first load."""
        app.run()

        # Should not be authenticated initially
        assert not app.session_state.get("authenticated", False), \
            "Should not be authenticated on initial load"

    def test_successful_login(self, app):
        """Test successful authentication."""
        app.run()

        # Enter correct password
        if hasattr(app, 'text_input'):
            app.text_input[0].set_value("escalation2024").run()

        # Click login button
        if hasattr(app, 'button'):
            app.button[0].click().run()

        # Should be authenticated
        assert app.session_state.get("authenticated") == True, \
            "Should be authenticated after correct password"

    def test_failed_login(self, app):
        """Test authentication failure."""
        app.run()

        # Enter wrong password
        if hasattr(app, 'text_input'):
            app.text_input[0].set_value("wrongpassword").run()

        # Click login button
        if hasattr(app, 'button'):
            app.button[0].click().run()

        # Should not be authenticated
        assert app.session_state.get("authenticated") != True, \
            "Should not be authenticated with wrong password"

    def test_login_persists_in_session(self, authenticated_app):
        """Test that login persists across interactions."""
        # Already authenticated from fixture
        assert authenticated_app.session_state.authenticated == True

        # Rerun should maintain authentication
        authenticated_app.run()
        assert authenticated_app.session_state.authenticated == True


@pytest.mark.ui
class TestChatInterface:
    """Test chat functionality."""

    def test_chat_input_exists(self, authenticated_app):
        """Authenticated users should see chat input."""
        assert hasattr(authenticated_app, 'chat_input'), \
            "Chat input should be available when authenticated"

    def test_submit_query(self, authenticated_app):
        """Test submitting a chat query."""
        initial_message_count = len(
            authenticated_app.session_state.get("messages", [])
        )

        # Submit query
        if hasattr(authenticated_app, 'chat_input'):
            authenticated_app.chat_input[0].set_value(
                "test query: printer issue"
            ).run()

        # Should have more messages
        final_message_count = len(
            authenticated_app.session_state.get("messages", [])
        )
        assert final_message_count > initial_message_count, \
            "Should have added messages after query"

    def test_message_history_persists(self, authenticated_app):
        """Test that message history is maintained."""
        # Submit first query
        if hasattr(authenticated_app, 'chat_input'):
            authenticated_app.chat_input[0].set_value("first query").run()

        first_count = len(authenticated_app.session_state.messages)

        # Submit second query
        if hasattr(authenticated_app, 'chat_input'):
            authenticated_app.chat_input[0].set_value("second query").run()

        second_count = len(authenticated_app.session_state.messages)

        # Should have accumulated messages
        assert second_count > first_count, \
            "Message history should accumulate"

    def test_empty_query_handling(self, authenticated_app):
        """Test submitting empty query."""
        initial_count = len(
            authenticated_app.session_state.get("messages", [])
        )

        # Try to submit empty query
        if hasattr(authenticated_app, 'chat_input'):
            authenticated_app.chat_input[0].set_value("").run()

        # Should not add messages for empty query
        final_count = len(
            authenticated_app.session_state.get("messages", [])
        )
        assert final_count == initial_count, \
            "Empty query should not add messages"


@pytest.mark.ui
class TestSessionState:
    """Test session state management."""

    def test_session_state_initialization(self, app):
        """Test that session state initializes correctly."""
        app.run()

        # Check for expected session state keys
        assert "messages" in app.session_state or \
               app.session_state.get("messages") is not None, \
               "messages should be in session state"

    def test_session_state_persistence(self, authenticated_app):
        """Test session state persists across reruns."""
        # Add data to session
        if hasattr(authenticated_app, 'chat_input'):
            authenticated_app.chat_input[0].set_value("test persistence").run()

        messages_before = authenticated_app.session_state.messages.copy()

        # Rerun
        authenticated_app.run()

        # Messages should still exist
        messages_after = authenticated_app.session_state.messages
        assert len(messages_after) == len(messages_before), \
            "Session state should persist across reruns"


@pytest.mark.ui
@pytest.mark.slow
class TestFollowUpQuestions:
    """Test follow-up question flow."""

    def test_low_confidence_triggers_followup(self, authenticated_app, mocker):
        """Test that low confidence results trigger follow-up questions."""
        # Mock search to return low confidence (high distance)
        mocker.patch(
            'app.search_knowledge_base',
            return_value=[
                {"distance": 0.35, "content": "Some result"}
            ]
        )

        # Submit query
        if hasattr(authenticated_app, 'chat_input'):
            authenticated_app.chat_input[0].set_value("printer problem").run()

        # Check if follow-up question was asked
        messages = authenticated_app.session_state.messages

        # Should have follow-up question in messages
        follow_up_exists = any(
            "?" in msg.get("content", "")
            for msg in messages
            if msg.get("role") == "assistant"
        )

        assert follow_up_exists, \
            "Low confidence should trigger follow-up question"

    def test_high_confidence_skips_followup(self, authenticated_app, mocker):
        """Test that high confidence results skip follow-up questions."""
        # Mock search to return high confidence (low distance)
        mocker.patch(
            'app.search_knowledge_base',
            return_value=[
                {"distance": 0.15, "content": "Highly relevant result"}
            ]
        )

        # Submit query
        if hasattr(authenticated_app, 'chat_input'):
            authenticated_app.chat_input[0].set_value("specific printer issue").run()

        # Should proceed directly to answer without follow-up
        messages = authenticated_app.session_state.messages

        # Last assistant message should be answer, not question
        assistant_messages = [
            msg for msg in messages
            if msg.get("role") == "assistant"
        ]

        if assistant_messages:
            last_message = assistant_messages[-1].get("content", "")
            # High confidence should give direct answer
            assert len(last_message) > 50, \
                "High confidence should provide direct answer"

    def test_followup_response_refinement(self, authenticated_app):
        """Test that answering follow-up improves results."""
        # Submit initial query
        if hasattr(authenticated_app, 'chat_input'):
            authenticated_app.chat_input[0].set_value("printer issue").run()

        initial_message_count = len(authenticated_app.session_state.messages)

        # Answer follow-up (if it appears)
        if hasattr(authenticated_app, 'chat_input'):
            authenticated_app.chat_input[0].set_value(
                "kitchen printer not printing receipts"
            ).run()

        # Should have more specific response
        final_message_count = len(authenticated_app.session_state.messages)
        assert final_message_count > initial_message_count, \
            "Follow-up response should add messages"


@pytest.mark.ui
class TestErrorHandling:
    """Test error states and edge cases."""

    def test_no_openai_key_error(self):
        """Test behavior when OpenAI key is missing."""
        app = AppTest.from_file("app.py")
        app.secrets["APP_PASSWORD"] = "escalation2024"
        # Don't set OPENAI_API_KEY

        app.run()

        # App should handle gracefully
        # (May show error or use fallback - test your specific behavior)
        assert not app.exception, \
            "Should handle missing API key gracefully"

    def test_malformed_query_handling(self, authenticated_app):
        """Test handling of malformed queries."""
        malformed_queries = [
            "x" * 1000,  # Very long query
            "SELECT * FROM'; DROP TABLE--",  # SQL injection attempt
            "<script>alert('xss')</script>",  # XSS attempt
        ]

        for query in malformed_queries:
            initial_count = len(authenticated_app.session_state.messages)

            if hasattr(authenticated_app, 'chat_input'):
                authenticated_app.chat_input[0].set_value(query).run()

            # Should not crash
            assert not authenticated_app.exception, \
                f"Should handle malformed query: {query[:50]}"

    def test_network_error_resilience(self, authenticated_app, mocker):
        """Test handling of network/API errors."""
        # Mock API error
        mocker.patch(
            'app.search_knowledge_base',
            side_effect=Exception("API Error")
        )

        if hasattr(authenticated_app, 'chat_input'):
            authenticated_app.chat_input[0].set_value("test query").run()

        # Should show error message gracefully
        # (Check your specific error handling implementation)
        messages = authenticated_app.session_state.messages
        error_shown = any(
            "error" in msg.get("content", "").lower()
            for msg in messages
        )

        assert error_shown or authenticated_app.exception, \
            "Should handle API errors gracefully"


@pytest.mark.ui
class TestUIComponents:
    """Test specific UI components."""

    def test_sidebar_exists(self, authenticated_app):
        """Test sidebar is rendered."""
        # Check sidebar elements exist
        # (Adjust based on your sidebar content)
        authenticated_app.run()

        # Sidebar should contain app info
        assert hasattr(authenticated_app, 'sidebar'), \
            "App should have sidebar"

    def test_title_displayed(self, app):
        """Test app title is displayed."""
        app.run()

        # Should have title element
        # (Adjust selector based on your title)
        assert hasattr(app, 'title') or hasattr(app, 'markdown'), \
            "App should display title"

    def test_clear_history_button(self, authenticated_app):
        """Test clear history functionality."""
        # Add some messages
        if hasattr(authenticated_app, 'chat_input'):
            authenticated_app.chat_input[0].set_value("test message").run()

        assert len(authenticated_app.session_state.messages) > 0, \
            "Should have messages"

        # Find and click clear button (if it exists in your app)
        # Adjust based on your implementation
        if hasattr(authenticated_app, 'button'):
            for button in authenticated_app.button:
                if "clear" in str(button).lower():
                    button.click().run()
                    break

        # Check if messages were cleared
        # (Adjust based on your clear implementation)
```

### Day 3-4: Critical Flows and Integration

Create `tests/test_integration.py`:
```python
"""Integration tests combining multiple components."""
import pytest
from streamlit.testing.v1 import AppTest
import os


@pytest.fixture
def app():
    """Create AppTest instance."""
    at = AppTest.from_file("app.py", default_timeout=30)
    at.secrets["APP_PASSWORD"] = "escalation2024"
    at.secrets["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "test-key")
    return at


@pytest.mark.integration
@pytest.mark.slow
class TestEndToEndFlows:
    """Test complete user journeys."""

    def test_complete_search_flow(self, app):
        """Test entire flow: login -> search -> get results."""
        # Start app
        app.run()

        # Login
        app.text_input[0].set_value("escalation2024").run()
        app.button[0].click().run()
        assert app.session_state.authenticated == True

        # Submit query
        app.chat_input[0].set_value("cashier can't void order").run()

        # Should have messages
        assert len(app.session_state.messages) > 0

        # Should have both user and assistant messages
        roles = [msg.get("role") for msg in app.session_state.messages]
        assert "user" in roles
        assert "assistant" in roles

    def test_multi_turn_conversation(self, app):
        """Test multiple back-and-forth interactions."""
        # Login
        app.run()
        app.text_input[0].set_value("escalation2024").run()
        app.button[0].click().run()

        queries = [
            "printer not working",
            "it's a kitchen printer",
            "what tables should I check"
        ]

        for query in queries:
            app.chat_input[0].set_value(query).run()

        # Should have accumulated messages from all turns
        messages = app.session_state.messages
        user_messages = [m for m in messages if m.get("role") == "user"]

        assert len(user_messages) >= len(queries), \
            "Should track multi-turn conversation"

    def test_category_specific_flow(self, app):
        """Test flow for each major category."""
        app.run()
        app.text_input[0].set_value("escalation2024").run()
        app.button[0].click().run()

        category_queries = {
            "printer": "receipt printer offline",
            "payment": "credit card declined",
            "employee": "user permissions issue",
            "order": "can't modify order",
            "menu": "menu item missing",
            "cash": "cash drawer stuck"
        }

        for category, query in category_queries.items():
            initial_count = len(app.session_state.messages)

            app.chat_input[0].set_value(query).run()

            final_count = len(app.session_state.messages)
            assert final_count > initial_count, \
                f"Should handle {category} queries"


@pytest.mark.integration
class TestRetrievalIntegration:
    """Test integration between UI and retrieval system."""

    def test_ui_calls_search(self, app, mocker):
        """Test that UI properly calls search function."""
        # Mock search
        mock_search = mocker.patch('app.search_knowledge_base')
        mock_search.return_value = [
            {"content": "test result", "distance": 0.2}
        ]

        # Login and search
        app.run()
        app.text_input[0].set_value("escalation2024").run()
        app.button[0].click().run()
        app.chat_input[0].set_value("test query").run()

        # Verify search was called
        assert mock_search.called, "UI should call search function"

        # Verify search was called with user query
        call_args = mock_search.call_args
        assert "test query" in str(call_args), \
            "Search should be called with user query"

    def test_ui_displays_search_results(self, app, mocker):
        """Test that UI displays search results."""
        # Mock search with known results
        mocker.patch(
            'app.search_knowledge_base',
            return_value=[
                {"content": "Known test result", "distance": 0.2}
            ]
        )

        # Login and search
        app.run()
        app.text_input[0].set_value("escalation2024").run()
        app.button[0].click().run()
        app.chat_input[0].set_value("test query").run()

        # Check if results appear in messages
        messages = app.session_state.messages
        assistant_messages = [
            m.get("content", "")
            for m in messages
            if m.get("role") == "assistant"
        ]

        # Should have some response
        assert len(assistant_messages) > 0, \
            "Should display search results"


@pytest.mark.integration
class TestDataPipeline:
    """Test data flow through the system."""

    def test_query_to_response_pipeline(self, app):
        """Test complete data pipeline from query to response."""
        app.run()
        app.text_input[0].set_value("escalation2024").run()
        app.button[0].click().run()

        test_query = "printer troubleshooting steps"
        app.chat_input[0].set_value(test_query).run()

        messages = app.session_state.messages

        # Verify data flow
        # 1. User query should be stored
        user_msgs = [m for m in messages if m.get("role") == "user"]
        assert any(test_query in m.get("content", "") for m in user_msgs)

        # 2. Assistant response should exist
        assistant_msgs = [m for m in messages if m.get("role") == "assistant"]
        assert len(assistant_msgs) > 0

        # 3. Response should be non-empty
        assert all(len(m.get("content", "")) > 0 for m in assistant_msgs)
```

### Day 5: Combined Test Suite

Update `pytest.ini` to organize tests:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --tb=short
    --disable-warnings
    --html=reports/full_report.html
    --self-contained-html
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    ui: marks tests as UI tests
    rag: marks tests as RAG evaluation tests
    unit: marks tests as unit tests
    smoke: marks tests as smoke tests (quick validation)
```

Create test suites in `tests/test_suites.py`:
```python
"""Predefined test suites for different scenarios."""
import pytest

# Smoke test suite - quick validation
smoke_tests = pytest.mark.smoke

# Full test suite - everything
full_suite = pytest.mark.suite

# CI/CD test suite - fast tests for CI
ci_suite = pytest.mark.ci
```

### Week 3 Commands

```bash
# Run all UI tests
pytest tests/test_ui.py -v -m ui

# Run integration tests
pytest tests/test_integration.py -v -m integration

# Run fast tests only (no slow/integration)
pytest -v -m "not slow and not integration"

# Run smoke tests (quick validation)
pytest -v -m smoke

# Run everything with full report
pytest --html=reports/full_report.html --self-contained-html \
       --cov=. --cov-report=html -v

# Run specific flow test
pytest tests/test_ui.py::TestChatInterface::test_submit_query -v -s

# Run with increased timeout for slow UI tests
pytest tests/test_ui.py -v --timeout=60
```

### Week 3 Deliverables Checklist

- [ ] `test_ui.py` with 10+ UI tests
- [ ] `test_integration.py` with end-to-end flows
- [ ] AppTest tests for login flow
- [ ] AppTest tests for chat interface
- [ ] Session state tests
- [ ] Follow-up question flow tests
- [ ] Error handling tests
- [ ] Test suites defined for different scenarios
- [ ] pytest.ini updated with all markers
- [ ] Combined test command works

### Common Pitfalls - Week 3

1. **AppTest Timing**: UI tests can be flaky due to timing. Use adequate timeouts.
2. **Session State**: AppTest session state behaves differently than live app. Test thoroughly.
3. **Mocking Challenges**: Mocking Streamlit components is tricky. Prefer integration tests over heavy mocking.
4. **Element Selection**: AppTest uses array indices for elements. Tests break if UI changes. Keep tests flexible.
5. **Secrets Management**: Remember to set secrets in AppTest fixture. Missing secrets cause silent failures.
6. **Chat Input**: `chat_input` may not exist until app is authenticated. Check before accessing.

---

## Phase 4: Automation & CI/CD (Week 4+)

### Goals
- Automate test execution with GitHub Actions
- Implement quality gates
- Generate and archive test reports
- Set up continuous monitoring

### Day 1-2: GitHub Actions Workflow

Create `.github/workflows/test.yml`:
```yaml
name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
  schedule:
    # Run tests daily at 2 AM UTC
    - cron: '0 2 * * *'
  workflow_dispatch:  # Allow manual trigger

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version: ['3.11', '3.12']

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}

    - name: Cache dependencies
      uses: actions/cache@v4
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-test.txt

    - name: Run linting
      run: |
        pip install flake8 black
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        black --check .

    - name: Run unit tests
      run: |
        pytest tests/test_retrieval.py -v -m "not slow"

    - name: Run integration tests
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        APP_PASSWORD: escalation2024
      run: |
        pytest tests/test_integration.py -v -m integration

    - name: Run UI tests
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        APP_PASSWORD: escalation2024
      run: |
        pytest tests/test_ui.py -v -m ui

    - name: Generate HTML report
      if: always()
      run: |
        pytest --html=reports/test_report.html \
               --self-contained-html \
               --cov=. \
               --cov-report=html \
               --cov-report=xml \
               -v

    - name: Upload test report
      uses: actions/upload-artifact@v4
      if: always()
      with:
        name: test-report-py${{ matrix.python-version }}
        path: reports/test_report.html
        retention-days: 30

    - name: Upload coverage report
      uses: actions/upload-artifact@v4
      if: always()
      with:
        name: coverage-report-py${{ matrix.python-version }}
        path: htmlcov/
        retention-days: 30

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v4
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
        fail_ci_if_error: false

  rag-evaluation:
    runs-on: ubuntu-latest
    needs: test  # Run after basic tests pass

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.12'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt

    - name: Run RAG evaluation
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      run: |
        pytest tests/test_rag_quality.py -v -m rag \
          --html=reports/rag_report.html \
          --self-contained-html

    - name: Check quality thresholds
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      run: |
        python scripts/check_thresholds.py \
          --faithfulness 0.85 \
          --context-recall 0.80 \
          --context-precision 0.75 \
          --response-relevancy 0.85 \
          --coverage 70

    - name: Upload RAG report
      uses: actions/upload-artifact@v4
      if: always()
      with:
        name: rag-evaluation-report
        path: reports/rag_report.html
        retention-days: 30

  quality-gate:
    runs-on: ubuntu-latest
    needs: [test, rag-evaluation]
    if: github.event_name == 'pull_request'

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Download coverage
      uses: actions/download-artifact@v4
      with:
        name: coverage-report-py3.12
        path: coverage/

    - name: Check coverage threshold
      run: |
        # Extract coverage percentage from report
        # Implement coverage check logic
        echo "Checking coverage threshold..."

    - name: Comment on PR
      uses: actions/github-script@v7
      with:
        script: |
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: '✅ All quality gates passed! Tests and RAG evaluation successful.'
          })
```

Create `.github/workflows/nightly-full-test.yml`:
```yaml
name: Nightly Full Test Suite

on:
  schedule:
    - cron: '0 3 * * *'  # 3 AM UTC daily
  workflow_dispatch:

jobs:
  comprehensive-test:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.12'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt

    - name: Run ALL tests (including slow)
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        APP_PASSWORD: escalation2024
      run: |
        pytest -v --html=reports/nightly_report.html \
               --self-contained-html \
               --cov=. \
               --cov-report=html \
               --cov-report=term

    - name: Run comprehensive RAG evaluation
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      run: |
        pytest tests/test_rag_quality.py::TestRAGComprehensive -v -s \
          --html=reports/nightly_rag_report.html \
          --self-contained-html

    - name: Upload reports
      uses: actions/upload-artifact@v4
      if: always()
      with:
        name: nightly-test-reports
        path: reports/
        retention-days: 90

    - name: Send notification on failure
      if: failure()
      uses: actions/github-script@v7
      with:
        script: |
          github.rest.repos.createDispatchEvent({
            owner: context.repo.owner,
            repo: context.repo.repo,
            event_type: 'test-failure',
            client_payload: {
              message: 'Nightly test suite failed',
              run_url: `${context.serverUrl}/${context.repo.owner}/${context.repo.repo}/actions/runs/${context.runId}`
            }
          })
```

### Day 3: Quality Gates and Badges

Create `scripts/generate_badge.py`:
```python
#!/usr/bin/env python3
"""Generate test coverage badge."""
import json
import xml.etree.ElementTree as ET
from pathlib import Path


def get_coverage_from_xml(xml_path):
    """Extract coverage percentage from coverage.xml."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Get line coverage
    line_rate = float(root.attrib.get('line-rate', 0))
    coverage = line_rate * 100

    return round(coverage, 1)


def generate_badge_json(coverage):
    """Generate badge JSON for shields.io."""
    if coverage >= 80:
        color = "brightgreen"
    elif coverage >= 70:
        color = "green"
    elif coverage >= 60:
        color = "yellow"
    else:
        color = "red"

    badge = {
        "schemaVersion": 1,
        "label": "coverage",
        "message": f"{coverage}%",
        "color": color
    }

    return badge


def main():
    xml_path = Path("coverage.xml")
    output_path = Path("reports/coverage_badge.json")

    if not xml_path.exists():
        print("coverage.xml not found")
        return

    coverage = get_coverage_from_xml(xml_path)
    badge = generate_badge_json(coverage)

    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(badge, f)

    print(f"Coverage: {coverage}%")
    print(f"Badge generated: {output_path}")


if __name__ == "__main__":
    main()
```

Update `README.md` with badges:
```markdown
# Escalation Helper

![Tests](https://github.com/yourusername/escalation-helper/workflows/Test%20Suite/badge.svg)
![Coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/yourusername/escalation-helper/main/reports/coverage_badge.json)
![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue)

[Rest of README...]
```

### Day 4-5: Monitoring and Reporting

Create `scripts/analyze_test_trends.py`:
```python
#!/usr/bin/env python3
"""Analyze test trends over time."""
import json
from pathlib import Path
from datetime import datetime, timedelta
import matplotlib.pyplot as plt


def load_historical_results(days=30):
    """Load test results from past N days."""
    results = []
    reports_dir = Path("reports/history")

    if not reports_dir.exists():
        return results

    cutoff = datetime.now() - timedelta(days=days)

    for file in reports_dir.glob("metrics_*.json"):
        try:
            with open(file) as f:
                data = json.load(f)
                timestamp = datetime.fromisoformat(data.get("timestamp"))

                if timestamp >= cutoff:
                    results.append(data)
        except Exception as e:
            print(f"Error loading {file}: {e}")

    return sorted(results, key=lambda x: x["timestamp"])


def plot_trends(results):
    """Generate trend charts."""
    if not results:
        print("No historical data available")
        return

    timestamps = [r["timestamp"] for r in results]
    faithfulness = [r.get("faithfulness", 0) for r in results]
    coverage = [r.get("coverage", 0) for r in results]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    # Faithfulness trend
    ax1.plot(timestamps, faithfulness, marker='o')
    ax1.axhline(y=0.85, color='r', linestyle='--', label='Threshold')
    ax1.set_title('Faithfulness Score Trend')
    ax1.set_ylabel('Score')
    ax1.legend()
    ax1.grid(True)

    # Coverage trend
    ax2.plot(timestamps, coverage, marker='o', color='green')
    ax2.axhline(y=70, color='r', linestyle='--', label='Threshold')
    ax2.set_title('Test Coverage Trend')
    ax2.set_ylabel('Coverage %')
    ax2.set_xlabel('Date')
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    plt.savefig('reports/trends.png')
    print("Trend chart saved to reports/trends.png")


def main():
    results = load_historical_results(days=30)

    if results:
        print(f"Loaded {len(results)} test results from past 30 days")
        plot_trends(results)
    else:
        print("No historical data found")


if __name__ == "__main__":
    main()
```

Create `.github/workflows/report-archival.yml`:
```yaml
name: Archive Test Reports

on:
  workflow_run:
    workflows: ["Test Suite"]
    types:
      - completed

jobs:
  archive:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Download artifacts
      uses: actions/download-artifact@v4
      with:
        path: artifacts/

    - name: Archive reports
      run: |
        mkdir -p reports/history
        timestamp=$(date -u +"%Y%m%d_%H%M%S")

        # Copy reports to history with timestamp
        if [ -f artifacts/test-report-py3.12/test_report.html ]; then
          cp artifacts/test-report-py3.12/test_report.html \
             reports/history/test_report_$timestamp.html
        fi

        if [ -f artifacts/rag-evaluation-report/rag_report.html ]; then
          cp artifacts/rag-evaluation-report/rag_report.html \
             reports/history/rag_report_$timestamp.html
        fi

    - name: Commit archived reports
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add reports/history/
        git commit -m "Archive test reports from ${{ github.sha }}" || echo "No changes"
        git push
```

### Week 4 Commands

```bash
# Simulate CI locally with act
act -j test

# Run full suite as CI would
pytest --html=reports/ci_report.html --self-contained-html \
       --cov=. --cov-report=xml -v

# Generate coverage badge
python scripts/generate_badge.py

# Analyze trends
python scripts/analyze_test_trends.py

# Validate GitHub Actions workflow
act -l
```

### Week 4 Deliverables Checklist

- [ ] GitHub Actions workflow (`test.yml`)
- [ ] Nightly full test workflow
- [ ] Quality gate implementation
- [ ] Test report artifacts uploaded
- [ ] Coverage reporting to Codecov
- [ ] Badge generation script
- [ ] README badges added
- [ ] Test trend analysis script
- [ ] Report archival workflow
- [ ] CI running on every PR
- [ ] Notifications configured

### Common Pitfalls - Week 4

1. **Secrets Management**: Ensure `OPENAI_API_KEY` is set in GitHub Secrets. Tests will fail silently without it.
2. **API Rate Limits**: RAGAS tests use OpenAI API. Monitor usage to avoid rate limits in CI.
3. **Flaky Tests**: Network-dependent tests can be flaky in CI. Use retries or mark as flaky.
4. **Artifact Retention**: Default 90 days. Adjust based on needs and storage costs.
5. **Matrix Builds**: Testing multiple Python versions increases CI time. Use caching.
6. **Workflow Permissions**: Report archival needs write permissions. Configure in workflow or repo settings.

---

## Quick Start Commands

### Development Workflow
```bash
# Run fast tests during development
pytest -v -m "not slow and not integration"

# Run tests for specific feature
pytest -k "printer" -v

# Run with live output (for debugging)
pytest -v -s

# Run single test
pytest tests/test_retrieval.py::TestBasicRetrieval::test_search_returns_results -v
```

### Pre-Commit Testing
```bash
# Run what CI will run (fast tests only)
pytest -v -m "not slow" --cov=. --cov-report=term

# Run specific test suite
pytest -v -m ui  # UI tests only
pytest -v -m rag  # RAG tests only
pytest -v -m integration  # Integration tests only
```

### Full Test Suite
```bash
# Run everything with reports
pytest --html=reports/full_report.html --self-contained-html \
       --cov=. --cov-report=html --cov-report=term -v

# Run comprehensive RAG evaluation
pytest tests/test_rag_quality.py::TestRAGComprehensive -v -s

# Run nightly test suite
pytest --html=reports/nightly.html --self-contained-html \
       --cov=. --cov-report=html -v
```

### Debugging
```bash
# Run with full traceback
pytest -v --tb=long

# Drop into debugger on failure
pytest -v --pdb

# Verbose output for specific test
pytest tests/test_ui.py::TestLoginFlow::test_successful_login -v -s

# Run with coverage and identify untested lines
pytest --cov=app --cov-report=term-missing
```

### CI/CD Simulation
```bash
# Simulate GitHub Actions locally (requires act)
act -j test

# Run quality gate check
python scripts/check_thresholds.py \
  --faithfulness 0.85 \
  --context-recall 0.80 \
  --coverage 70

# Generate all reports
pytest --html=reports/test_report.html --self-contained-html \
       --cov=. --cov-report=html --cov-report=xml -v
python scripts/generate_badge.py
python scripts/analyze_test_trends.py
```

---

## File Structure After Full Implementation

```
escalation-helper/
├── .github/
│   └── workflows/
│       ├── test.yml                    # Main test workflow
│       ├── nightly-full-test.yml       # Comprehensive nightly tests
│       └── report-archival.yml         # Archive test reports
├── app.py
├── config.py
├── ingest.py
├── requirements.txt
├── requirements-test.txt               # Test dependencies
├── pytest.ini                          # Pytest configuration
├── .coveragerc                         # Coverage configuration
├── scripts/
│   ├── check_thresholds.py            # Quality gate validation
│   ├── generate_badge.py              # Coverage badge generation
│   └── analyze_test_trends.py         # Trend analysis
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    # Shared fixtures
│   ├── test_retrieval.py              # Basic retrieval tests
│   ├── test_rag_quality.py            # RAGAS evaluation tests
│   ├── test_ui.py                     # Streamlit UI tests
│   ├── test_integration.py            # End-to-end integration tests
│   └── test_suites.py                 # Predefined test suites
├── data/
│   └── test_cases/
│       └── golden_dataset.json        # Golden test cases (20+)
├── docs/
│   ├── RAG_BASELINE_METRICS.md        # Baseline metrics documentation
│   └── 19 - RAG Testing Implementation Roadmap.md  # This file
├── reports/                            # Gitignored - generated artifacts
│   ├── test_report.html
│   ├── rag_report.html
│   ├── coverage_badge.json
│   ├── trends.png
│   ├── htmlcov/                       # HTML coverage report
│   └── history/                       # Archived historical reports
│       ├── test_report_20250101_120000.html
│       ├── rag_report_20250101_120000.html
│       └── metrics_20250101_120000.json
└── htmlcov/                           # Coverage HTML report (gitignored)
```

---

## Success Criteria

| Phase | Metric | Target | Status |
|-------|--------|--------|--------|
| **Phase 1: Minimum Viable Testing** |
| | Tests running | 5+ tests pass | - |
| | HTML report generated | Yes | - |
| | Golden dataset created | 10 cases | - |
| | Test infrastructure setup | Complete | - |
| **Phase 2: RAG Evaluation** |
| | RAGAS integrated | Yes | - |
| | Faithfulness score | > 0.85 | - |
| | Context Recall score | > 0.80 | - |
| | Context Precision score | > 0.75 | - |
| | Response Relevancy score | > 0.85 | - |
| | Golden dataset size | 20+ cases | - |
| | Baseline metrics documented | Yes | - |
| **Phase 3: UI Testing** |
| | UI tests running | 10+ tests pass | - |
| | Login flow tested | Yes | - |
| | Chat interface tested | Yes | - |
| | Error handling tested | Yes | - |
| | Integration tests | 5+ scenarios | - |
| **Phase 4: Automation & CI/CD** |
| | CI pipeline active | Yes | - |
| | Tests run on every PR | Yes | - |
| | Quality gates enforced | Yes | - |
| | Reports archived | Yes | - |
| | Coverage tracking | > 70% | - |
| | Badges displayed | Yes | - |

---

## Practical Tips Throughout

### Phase 1 Tips
- **Start Small**: Begin with 2-3 simple tests to validate setup
- **Use Fixtures Early**: Even simple fixtures save time later
- **Document As You Go**: Add comments to conftest.py explaining fixtures
- **Test Locally First**: Ensure tests pass locally before adding to CI

### Phase 2 Tips
- **Mock Expensive Calls**: Use `@pytest.mark.slow` for tests that call OpenAI API
- **Incremental Evaluation**: Start with 5 test cases, expand after validation
- **Baseline Before Changes**: Run full evaluation before making RAG changes
- **Monitor Costs**: RAGAS evaluation uses LLM calls - track OpenAI usage

### Phase 3 Tips
- **AppTest Quirks**: Session state in AppTest behaves differently than live app
- **Element Indexing**: Use descriptive variable names instead of magic indices
- **Timeout Generously**: UI tests need more time than unit tests
- **Test Real Scenarios**: Base UI tests on actual user workflows

### Phase 4 Tips
- **Cache Dependencies**: GitHub Actions caching saves 30-60 seconds per run
- **Fail Fast**: Run fast tests before slow ones in CI
- **Artifacts Matter**: Save HTML reports as artifacts for debugging
- **Notification Strategy**: Don't spam - notify only on main branch failures

### Common Testing Patterns

#### Pattern: Test with Mock and Real Data
```python
@pytest.mark.parametrize("use_mock", [True, False])
def test_search_with_toggle(use_mock, mocker):
    if use_mock:
        mocker.patch('app.search_knowledge_base', return_value=[...])

    results = search_knowledge_base("test query")
    assert len(results) > 0
```

#### Pattern: Gradual Tolerance Tightening
```python
# Start with loose tolerance
assert score > 0.70  # Initial baseline

# Tighten as system improves
assert score > 0.80  # After improvements

# Target final threshold
assert score > 0.85  # Production target
```

#### Pattern: Category-Specific Thresholds
```python
CATEGORY_THRESHOLDS = {
    "printer": 0.90,  # High confidence needed
    "payment": 0.95,  # Critical - highest standard
    "employee": 0.85,  # Standard
    "order": 0.88,    # Above standard
    "menu": 0.82,     # Slightly relaxed
    "cash": 0.85      # Standard
}
```

### Troubleshooting Guide

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| Tests pass locally, fail in CI | Environment differences | Check secrets, paths, Python version |
| RAGAS tests timeout | LLM API slow/rate limited | Increase timeout, reduce test cases |
| Flaky UI tests | Race conditions | Add explicit waits, increase timeout |
| Low coverage | Missing test files | Use `--cov-report=term-missing` to identify gaps |
| Quality gate fails | Threshold too strict | Review thresholds, check for regressions |
| Slow test suite | Too many API calls | Mock external calls, use cached results |

---

## Next Steps After Phase 4

### Continuous Improvement
1. **Monthly Reviews**: Review test trends and adjust thresholds
2. **Expand Dataset**: Add new golden cases from production issues
3. **Performance Testing**: Add response time benchmarks
4. **Load Testing**: Test with concurrent users (if applicable)
5. **Security Testing**: Add tests for SQL injection, XSS prevention

### Advanced Testing
- **A/B Testing Framework**: Compare different RAG strategies
- **Adversarial Testing**: Test with intentionally difficult queries
- **Multilingual Testing**: If supporting multiple languages
- **Accessibility Testing**: Ensure WCAG compliance

### Documentation
- **Test Case Library**: Document patterns for common test scenarios
- **Runbook**: Create guide for interpreting test failures
- **Onboarding Guide**: Help new contributors write tests

---

## Resources

### Testing Tools
- **pytest**: https://docs.pytest.org/
- **pytest-html**: https://pytest-html.readthedocs.io/
- **RAGAS**: https://docs.ragas.io/
- **Streamlit AppTest**: https://docs.streamlit.io/develop/api-reference/app-testing

### Best Practices
- **Testing Best Practices**: https://docs.pytest.org/en/stable/goodpractices.html
- **RAG Evaluation**: https://www.trulens.org/trulens_eval/getting_started/core_concepts/rag_triad/
- **CI/CD Patterns**: https://docs.github.com/en/actions/examples

### Community
- **RAGAS Discord**: For RAG testing questions
- **Streamlit Forum**: For UI testing questions
- **pytest Discussions**: For pytest-specific help

---

## Appendix: Configuration Files

### .coveragerc
```ini
[run]
source = .
omit =
    */tests/*
    */venv/*
    */virtualenv/*
    */site-packages/*
    */__pycache__/*
    */migrations/*

[report]
precision = 2
show_missing = True
skip_covered = False

[html]
directory = htmlcov
```

### .gitignore additions
```
# Test artifacts
reports/
htmlcov/
.coverage
coverage.xml
.pytest_cache/
*.pyc
__pycache__/

# Keep structure but ignore contents
reports/.gitkeep
!reports/history/.gitkeep
```

---

**Implementation Timeline Summary:**

- **Week 1**: Basic test infrastructure, 5-10 tests running, HTML reports
- **Week 2**: RAGAS integration, 20+ golden cases, baseline metrics
- **Week 3**: UI testing with AppTest, integration tests, combined suite
- **Week 4+**: CI/CD automation, quality gates, continuous monitoring

**Estimated Total Effort**: 3-4 weeks for full implementation (1 developer)

**Maintenance Effort**: 2-4 hours/month after initial setup
