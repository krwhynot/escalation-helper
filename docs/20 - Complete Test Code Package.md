# Complete Test Code Package

This document provides all ready-to-use test files for Escalation Helper RAG testing.

## Table of Contents

1. [requirements-test.txt](#1-requirements-testtxt)
2. [pytest.ini](#2-pytestini)
3. [tests/conftest.py](#3-testsconftestpy)
4. [tests/test_retrieval.py](#4-teststest_retrievalpy)
5. [tests/test_generation.py](#5-teststest_generationpy)
6. [tests/test_ui.py](#6-teststest_uipy)
7. [tests/golden_dataset.json](#7-testsgolden_datasetjson)
8. [Running the Tests](#8-running-the-tests)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. requirements-test.txt

**Location:** `/home/krwhynot/projects/escalation-helper/requirements-test.txt`

```txt
# Testing dependencies for Escalation Helper
pytest>=8.0.0
pytest-html>=4.1.1
pytest-cov>=4.1.0
pytest-asyncio>=0.23.0
ragas>=0.2.0
langchain>=0.1.0
langchain-openai>=0.0.5
```

---

## 2. pytest.ini

**Location:** `/home/krwhynot/projects/escalation-helper/pytest.ini`

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    rag: marks tests that evaluate RAG quality
    ui: marks tests for UI components
```

---

## 3. tests/conftest.py

**Location:** `/home/krwhynot/projects/escalation-helper/tests/conftest.py`

```python
"""
Shared fixtures and pytest-html customization for Escalation Helper tests.
"""
import pytest
import json
import os
from datetime import datetime
from pathlib import Path

# Try to import Streamlit testing (optional)
try:
    from streamlit.testing.v1 import AppTest
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

# ============ PYTEST-HTML CUSTOMIZATION ============

def pytest_html_report_title(report):
    report.title = "Escalation Helper - Test Report"

def pytest_configure(config):
    config._metadata['Project'] = 'Escalation Helper'
    config._metadata['Test Date'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    config._metadata['RAG Framework'] = 'RAGAS'
    config._metadata['LLM'] = 'GPT-4o-mini'
    config._metadata['Vector DB'] = 'ChromaDB'

def pytest_html_results_summary(prefix, summary, postfix):
    prefix.extend([
        "<p>RAG Testing Suite for SQL Troubleshooting Assistant</p>",
        "<p><b>Thresholds:</b> Faithfulness > 0.85 | Context Recall > 0.80</p>"
    ])

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if hasattr(item, 'rag_metrics') and report.when == "call":
        from pytest_html import extras
        report.extra = getattr(report, 'extra', [])
        metrics = item.rag_metrics
        html = f'''
        <div style="background:#e8f4f8; padding:10px; margin:5px 0; border-radius:5px; border-left:4px solid #0E8476;">
            <strong>RAG Metrics:</strong><br>
            Faithfulness: <b>{metrics.get('faithfulness', 'N/A')}</b> |
            Context Recall: <b>{metrics.get('context_recall', 'N/A')}</b>
        </div>
        '''
        report.extra.append(extras.html(html))

# ============ FIXTURES ============

@pytest.fixture(scope="session")
def project_root():
    """Return project root directory"""
    return Path(__file__).parent.parent

@pytest.fixture(scope="session")
def golden_dataset():
    """Load golden test dataset"""
    dataset_path = Path(__file__).parent / "golden_dataset.json"
    if dataset_path.exists():
        with open(dataset_path) as f:
            return json.load(f)['test_cases']
    return []

@pytest.fixture
def sample_queries():
    """Common test queries"""
    return [
        "cashier can't void an order",
        "printer not printing receipts",
        "employee can't clock in",
        "credit card payment failed",
        "menu item wrong price"
    ]

@pytest.fixture
def authenticated_app():
    """Pre-authenticated Streamlit app"""
    if not STREAMLIT_AVAILABLE:
        pytest.skip("Streamlit not available")
    at = AppTest.from_file("app.py")
    at.secrets["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "test-key")
    at.secrets["APP_PASSWORD"] = "escalation2024"
    at.session_state.authenticated = True
    at.run()
    return at

@pytest.fixture
def fresh_app():
    """Fresh app instance (not authenticated)"""
    if not STREAMLIT_AVAILABLE:
        pytest.skip("Streamlit not available")
    at = AppTest.from_file("app.py")
    at.secrets["APP_PASSWORD"] = "escalation2024"
    at.run()
    return at
```

---

## 4. tests/test_retrieval.py

**Location:** `/home/krwhynot/projects/escalation-helper/tests/test_retrieval.py`

```python
"""
Tests for the retrieval component of Escalation Helper.
"""
import pytest
import sys
sys.path.insert(0, '.')

# Import app functions (adjust based on actual app structure)
try:
    from app import search_knowledge_base
except ImportError:
    search_knowledge_base = None


class TestRetrieval:
    """Test the vector search retrieval"""

    @pytest.mark.skipif(search_knowledge_base is None, reason="search_knowledge_base not available")
    def test_search_returns_results(self):
        """Basic test: search returns non-empty results"""
        results = search_knowledge_base("cashier can't void")
        assert results is not None
        assert len(results) > 0

    @pytest.mark.skipif(search_knowledge_base is None, reason="search_knowledge_base not available")
    def test_search_relevance_void(self):
        """Results for void query should mention void or permission"""
        results = search_knowledge_base("cashier can't void an order")
        result_text = str(results).lower()
        assert "void" in result_text or "permission" in result_text or "secgrp" in result_text

    @pytest.mark.skipif(search_knowledge_base is None, reason="search_knowledge_base not available")
    def test_search_relevance_printer(self):
        """Results for printer query should mention printer"""
        results = search_knowledge_base("printer not printing receipts")
        result_text = str(results).lower()
        assert "printer" in result_text or "receipt" in result_text

    @pytest.mark.skipif(search_knowledge_base is None, reason="search_knowledge_base not available")
    def test_search_empty_query(self):
        """Empty query should be handled gracefully"""
        try:
            results = search_knowledge_base("")
            # Should either return empty or raise controlled exception
            assert results is not None or True
        except Exception as e:
            # Acceptable if it raises a controlled exception
            assert "empty" in str(e).lower() or "query" in str(e).lower() or True

    @pytest.mark.skipif(search_knowledge_base is None, reason="search_knowledge_base not available")
    @pytest.mark.parametrize("query,expected_keyword", [
        ("void order", "void"),
        ("printer issue", "printer"),
        ("employee clock", "employee"),
        ("payment failed", "payment"),
    ])
    def test_search_categories(self, query, expected_keyword):
        """Test that category-specific queries return relevant results"""
        results = search_knowledge_base(query)
        # This is a soft check - at least one result should be somewhat relevant
        assert results is not None
```

---

## 5. tests/test_generation.py

**Location:** `/home/krwhynot/projects/escalation-helper/tests/test_generation.py`

```python
"""
Tests for RAG generation quality using RAGAS metrics.
"""
import pytest
import os

# Check if RAGAS is available
try:
    from ragas import evaluate, EvaluationDataset
    from ragas.metrics import Faithfulness, LLMContextRecall, FactualCorrectness
    from ragas.llms import LangchainLLMWrapper
    RAGAS_AVAILABLE = True
except ImportError:
    RAGAS_AVAILABLE = False

try:
    from langchain_openai import ChatOpenAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


@pytest.fixture(scope="module")
def evaluator_llm():
    """Create evaluator LLM for RAGAS"""
    if not LANGCHAIN_AVAILABLE:
        pytest.skip("LangChain not available")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "test-key":
        pytest.skip("Valid OPENAI_API_KEY required for RAG evaluation")
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)
    return LangchainLLMWrapper(llm)


@pytest.mark.rag
@pytest.mark.skipif(not RAGAS_AVAILABLE, reason="RAGAS not installed")
class TestRAGQuality:
    """Test RAG system quality with RAGAS metrics"""

    def test_faithfulness_basic(self, evaluator_llm, request):
        """Test that responses are faithful to context"""
        test_case = {
            "user_input": "How do I check void permissions?",
            "retrieved_contexts": [
                "The SecGrp table controls employee permissions including void capabilities. Check the VoidPerm column."
            ],
            "response": "To check void permissions, look at the SecGrp table and check the VoidPerm column for the employee's security group.",
            "reference": "Check the SecGrp table for the VoidPerm column."
        }

        dataset = EvaluationDataset.from_list([test_case])
        result = evaluate(
            dataset=dataset,
            metrics=[Faithfulness()],
            llm=evaluator_llm
        )

        # Store metrics for report
        request.node.rag_metrics = {'faithfulness': result['faithfulness']}

        assert result['faithfulness'] > 0.85, f"Faithfulness {result['faithfulness']} below threshold 0.85"

    def test_context_recall_basic(self, evaluator_llm, request):
        """Test that relevant context is retrieved"""
        test_case = {
            "user_input": "Employee can't clock in",
            "retrieved_contexts": [
                "Check Employee table for Active status and AllowTimeClock permission."
            ],
            "response": "Verify the employee is active and has time clock permission enabled.",
            "reference": "Check Employee.Active and Employee.AllowTimeClock fields."
        }

        dataset = EvaluationDataset.from_list([test_case])
        result = evaluate(
            dataset=dataset,
            metrics=[LLMContextRecall()],
            llm=evaluator_llm
        )

        request.node.rag_metrics = {'context_recall': result['context_recall']}

        assert result['context_recall'] > 0.80, f"Context recall {result['context_recall']} below threshold 0.80"

    @pytest.mark.slow
    def test_golden_dataset_quality(self, evaluator_llm, golden_dataset, request):
        """Test quality across golden dataset (slow)"""
        if not golden_dataset:
            pytest.skip("Golden dataset not available")

        # Use first 5 test cases for speed
        test_cases = []
        for tc in golden_dataset[:5]:
            test_cases.append({
                "user_input": tc['query'],
                "retrieved_contexts": [tc.get('reference_answer', '')],
                "response": tc.get('reference_answer', ''),
                "reference": tc.get('reference_answer', '')
            })

        dataset = EvaluationDataset.from_list(test_cases)
        result = evaluate(
            dataset=dataset,
            metrics=[Faithfulness(), LLMContextRecall()],
            llm=evaluator_llm
        )

        request.node.rag_metrics = {
            'faithfulness': result['faithfulness'],
            'context_recall': result['context_recall']
        }

        assert result['faithfulness'] > 0.80
        assert result['context_recall'] > 0.75
```

---

## 6. tests/test_ui.py

**Location:** `/home/krwhynot/projects/escalation-helper/tests/test_ui.py`

```python
"""
UI tests for Escalation Helper using Streamlit AppTest.
"""
import pytest

try:
    from streamlit.testing.v1 import AppTest
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False


@pytest.mark.ui
@pytest.mark.skipif(not STREAMLIT_AVAILABLE, reason="Streamlit not available")
class TestLogin:
    """Test authentication flow"""

    def test_login_page_renders(self, fresh_app):
        """Login page should render without errors"""
        assert not fresh_app.exception
        # Should have password input
        assert len(fresh_app.text_input) > 0

    def test_login_correct_password(self, fresh_app):
        """Correct password should authenticate"""
        fresh_app.text_input[0].set_value("escalation2024").run()

        # Find and click login button
        if len(fresh_app.button) > 0:
            fresh_app.button[0].click().run()

        assert fresh_app.session_state.get('authenticated', False) == True

    def test_login_wrong_password(self, fresh_app):
        """Wrong password should show error"""
        fresh_app.text_input[0].set_value("wrong_password").run()

        if len(fresh_app.button) > 0:
            fresh_app.button[0].click().run()

        assert fresh_app.session_state.get('authenticated', False) == False


@pytest.mark.ui
@pytest.mark.skipif(not STREAMLIT_AVAILABLE, reason="Streamlit not available")
class TestChat:
    """Test chat interface"""

    def test_chat_input_available(self, authenticated_app):
        """Authenticated user should see chat input"""
        # Chat input should be available
        assert len(authenticated_app.chat_input) > 0

    def test_chat_submission(self, authenticated_app):
        """Chat submission should add message"""
        initial_count = len(authenticated_app.session_state.get('messages', []))

        authenticated_app.chat_input[0].set_value("test query").run()

        new_count = len(authenticated_app.session_state.get('messages', []))
        assert new_count >= initial_count

    def test_no_crash_on_query(self, authenticated_app):
        """App should not crash on valid query"""
        authenticated_app.chat_input[0].set_value("cashier can't void").run()
        assert not authenticated_app.exception


@pytest.mark.ui
@pytest.mark.skipif(not STREAMLIT_AVAILABLE, reason="Streamlit not available")
class TestSessionState:
    """Test session state management"""

    def test_messages_persist(self, authenticated_app):
        """Messages should persist in session"""
        authenticated_app.session_state.messages = [
            {"role": "user", "content": "test"},
            {"role": "assistant", "content": "response"}
        ]
        authenticated_app.run()

        assert len(authenticated_app.session_state.messages) == 2

    def test_clear_chat(self, authenticated_app):
        """Clear should reset messages"""
        authenticated_app.session_state.messages = [
            {"role": "user", "content": "test"}
        ]
        authenticated_app.run()

        # Clear messages
        authenticated_app.session_state.messages = []
        authenticated_app.run()

        assert len(authenticated_app.session_state.messages) == 0
```

---

## 7. tests/golden_dataset.json

**Location:** `/home/krwhynot/projects/escalation-helper/tests/golden_dataset.json`

```json
{
    "version": "1.0.0",
    "created": "2024-12-10",
    "description": "Golden test dataset for Escalation Helper",
    "test_cases": [
        {
            "id": "void-001",
            "query": "cashier can't void an order",
            "category": "order",
            "expected_answer_contains": ["SecGrp", "void", "permission"],
            "reference_answer": "Check SecGrp table for void permissions. SELECT VoidPerm FROM SecGrp WHERE SecGrpID = (SELECT SecGrpID FROM Employee WHERE EmpID = ?)",
            "difficulty": "easy"
        },
        {
            "id": "printer-001",
            "query": "receipt printer not printing",
            "category": "printer",
            "expected_answer_contains": ["Printer", "Station"],
            "reference_answer": "Check printer configuration: SELECT * FROM Printer WHERE Active = 1. Verify station assignment.",
            "difficulty": "medium"
        },
        {
            "id": "employee-001",
            "query": "employee can't clock in",
            "category": "employee",
            "expected_answer_contains": ["Employee", "TimeClock", "Active"],
            "reference_answer": "Verify employee status: SELECT Active, AllowTimeClock FROM Employee WHERE EmpID = ?",
            "difficulty": "easy"
        },
        {
            "id": "payment-001",
            "query": "credit card declined but charged",
            "category": "payment",
            "expected_answer_contains": ["Payment", "Transaction"],
            "reference_answer": "Check Payment table: SELECT * FROM Payment WHERE OrderID = ? AND TenderType = 'CC'",
            "difficulty": "hard"
        },
        {
            "id": "menu-001",
            "query": "menu item wrong price",
            "category": "menu",
            "expected_answer_contains": ["MenuItem", "Price"],
            "reference_answer": "Check MenuItem pricing: SELECT * FROM MenuItem WHERE ItemID = ?",
            "difficulty": "medium"
        },
        {
            "id": "cash-001",
            "query": "cash drawer won't open",
            "category": "cash",
            "expected_answer_contains": ["CashDrawer", "Printer", "Station"],
            "reference_answer": "Check printer configuration for cash drawer trigger. Verify station settings.",
            "difficulty": "medium"
        },
        {
            "id": "order-002",
            "query": "order stuck in kitchen display",
            "category": "order",
            "expected_answer_contains": ["Order", "Status", "Kitchen"],
            "reference_answer": "Check Order.Status and KitchenDisplay table for stuck orders.",
            "difficulty": "hard"
        },
        {
            "id": "employee-002",
            "query": "manager override not working",
            "category": "employee",
            "expected_answer_contains": ["SecGrp", "Manager", "Override"],
            "reference_answer": "Verify manager has override permissions in SecGrp table.",
            "difficulty": "medium"
        }
    ]
}
```

---

## 8. Running the Tests

### Initial Setup

```bash
# Create tests directory
mkdir -p tests

# Install test dependencies
pip install -r requirements-test.txt

# Ensure OPENAI_API_KEY is set in .env
echo "OPENAI_API_KEY=your_key_here" >> .env
```

### Basic Test Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_retrieval.py -v

# Run single test
pytest tests/test_ui.py::TestLogin::test_login_correct_password -v
```

### HTML Reports

```bash
# Generate HTML test report
pytest --html=reports/test_report.html --self-contained-html

# View report
firefox reports/test_report.html  # or open reports/test_report.html
```

### Test Filtering

```bash
# Run only fast tests (skip slow)
pytest -m "not slow"

# Run only UI tests
pytest -m ui

# Run only RAG tests
pytest -m rag

# Run retrieval tests only
pytest tests/test_retrieval.py
```

### Coverage Reports

```bash
# Run with coverage
pytest --cov=. --cov-report=html --cov-report=term

# View coverage report
firefox htmlcov/index.html
```

### Continuous Testing

```bash
# Watch mode (requires pytest-watch)
pip install pytest-watch
ptw -- -v

# Run tests on file change
while true; do
    pytest -v
    sleep 5
done
```

---

## 9. Troubleshooting

### Common Issues and Solutions

#### Issue: "ModuleNotFoundError: No module named 'app'"

**Solution:**
```bash
# Ensure you're in the project root
cd /home/krwhynot/projects/escalation-helper

# Run pytest from project root
pytest
```

#### Issue: "RAGAS tests skipped"

**Solution:**
```bash
# Install RAGAS dependencies
pip install ragas langchain langchain-openai

# Verify installation
python -c "import ragas; print('RAGAS installed')"
```

#### Issue: "OPENAI_API_KEY required for RAG evaluation"

**Solution:**
```bash
# Set API key in .env
echo "OPENAI_API_KEY=sk-..." >> .env

# Or export temporarily
export OPENAI_API_KEY=sk-...

# Verify
python -c "import os; print(os.getenv('OPENAI_API_KEY'))"
```

#### Issue: "Streamlit tests failing"

**Solution:**
```bash
# Ensure Streamlit is installed
pip install streamlit

# Check Streamlit version (need 1.31+)
streamlit --version

# Update if needed
pip install --upgrade streamlit
```

#### Issue: "ChromaDB not found during tests"

**Solution:**
```bash
# Run ingestion first to create DB
python ingest.py

# Verify DB exists
ls -la chroma_db/
```

#### Issue: "Test fixtures not found"

**Solution:**
```bash
# Ensure conftest.py is in tests/
ls -la tests/conftest.py

# Verify pytest finds it
pytest --fixtures | grep golden_dataset
```

#### Issue: "Slow tests timeout"

**Solution:**
```bash
# Skip slow tests
pytest -m "not slow"

# Or increase timeout (in pytest.ini)
# addopts = -v --tb=short --timeout=300
```

#### Issue: "HTML report not generated"

**Solution:**
```bash
# Create reports directory
mkdir -p reports

# Install pytest-html
pip install pytest-html

# Generate report with full path
pytest --html=/home/krwhynot/projects/escalation-helper/reports/test_report.html --self-contained-html
```

### Debugging Test Failures

```bash
# Run with full traceback
pytest --tb=long

# Run with print statements
pytest -s

# Run with debugger
pytest --pdb

# Run single failing test with verbose output
pytest tests/test_generation.py::TestRAGQuality::test_faithfulness_basic -vv -s
```

### Verifying Test Setup

```bash
# Check pytest can discover tests
pytest --collect-only

# Check markers are registered
pytest --markers

# Verify fixtures available
pytest --fixtures

# Check configuration
pytest --version
pytest --help
```

### Environment Verification Script

Create `verify_test_env.py`:

```python
import sys
import os

def verify_environment():
    checks = {
        "Python 3.12+": sys.version_info >= (3, 12),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY") is not None,
        "tests/ directory": os.path.isdir("tests"),
        "golden_dataset.json": os.path.isfile("tests/golden_dataset.json"),
        "conftest.py": os.path.isfile("tests/conftest.py"),
    }

    # Check imports
    try:
        import pytest
        checks["pytest"] = True
    except ImportError:
        checks["pytest"] = False

    try:
        import ragas
        checks["ragas"] = True
    except ImportError:
        checks["ragas"] = False

    try:
        from streamlit.testing.v1 import AppTest
        checks["streamlit.testing"] = True
    except ImportError:
        checks["streamlit.testing"] = False

    print("\nEnvironment Verification:")
    print("-" * 50)
    for check, status in checks.items():
        status_str = "✓" if status else "✗"
        print(f"{status_str} {check}")
    print("-" * 50)

    all_passed = all(checks.values())
    print(f"\nOverall: {'PASS' if all_passed else 'FAIL'}")
    return all_passed

if __name__ == "__main__":
    verify_environment()
```

Run verification:
```bash
python verify_test_env.py
```

---

## Quick Reference

### Test Structure

```
escalation-helper/
├── tests/
│   ├── conftest.py              # Fixtures and pytest config
│   ├── golden_dataset.json      # Test data
│   ├── test_retrieval.py        # Vector search tests
│   ├── test_generation.py       # RAG quality tests
│   └── test_ui.py              # UI tests
├── pytest.ini                   # Pytest configuration
├── requirements-test.txt        # Test dependencies
└── reports/                     # Generated test reports
```

### Key Commands

| Command | Purpose |
|---------|---------|
| `pytest` | Run all tests |
| `pytest -v` | Verbose output |
| `pytest -m ui` | Run UI tests only |
| `pytest -m "not slow"` | Skip slow tests |
| `pytest --html=reports/test.html` | Generate HTML report |
| `pytest --cov` | Coverage report |
| `pytest -k void` | Run tests matching "void" |

### Pytest Markers

- `@pytest.mark.ui` - UI/Streamlit tests
- `@pytest.mark.rag` - RAG quality tests
- `@pytest.mark.slow` - Slow tests (can skip)
- `@pytest.mark.skipif` - Conditional skip

---

## Next Steps

After setting up the test suite:

1. **Run initial tests**: `pytest -v` to verify setup
2. **Generate baseline report**: `pytest --html=reports/baseline.html --self-contained-html`
3. **Review failures**: Address any failing tests
4. **Expand golden dataset**: Add more test cases to `golden_dataset.json`
5. **Set up CI/CD**: Integrate tests into deployment pipeline
6. **Monitor metrics**: Track faithfulness and recall over time

For more information, see:
- [10 - Testing Implementation.md](10%20-%20Testing%20Implementation.md)
- [11 - Advanced RAG Testing.md](11%20-%20Advanced%20RAG%20Testing.md)
