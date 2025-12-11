"""
================================================
Escalation Helper - Pytest Configuration
================================================
Shared fixtures and test configuration for the
Escalation Helper test suite.
================================================
"""

import pytest
import json
import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# ================================================
# pytest-html Customization
# ================================================

def pytest_html_report_title(report):
    """Customize the HTML report title."""
    report.title = "Escalation Helper - Test Report"


def pytest_configure(config):
    """Configure pytest metadata for HTML reports."""
    config._metadata = {
        "Project": "Escalation Helper",
        "Description": "AI-powered SQL troubleshooting assistant",
        "Test Environment": os.getenv("TEST_ENV", "development"),
        "Python Version": f"{config.option.verbose}",
        "ChromaDB Path": "./chroma_db",
        "Embedding Model": "text-embedding-ada-002",
        "LLM Model": "gpt-4o-mini",
    }


def pytest_html_results_table_header(cells):
    """Add custom columns to HTML report table."""
    cells.insert(2, '<th>RAG Metrics</th>')


def pytest_html_results_table_row(report, cells):
    """Add RAG metrics to HTML report rows."""
    if hasattr(report, 'rag_metrics'):
        metrics = report.rag_metrics
        metrics_html = f"""
        <div style="font-size: 0.9em;">
            <div>Similarity: {metrics.get('similarity', 'N/A')}</div>
            <div>Retrieval: {metrics.get('retrieval_time', 'N/A')}ms</div>
            <div>Results: {metrics.get('num_results', 'N/A')}</div>
        </div>
        """
        cells.insert(2, f'<td>{metrics_html}</td>')
    else:
        cells.insert(2, '<td>N/A</td>')


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture RAG metrics in test reports."""
    outcome = yield
    report = outcome.get_result()

    # Attach RAG metrics if present in the test
    if hasattr(item, 'rag_metrics'):
        report.rag_metrics = item.rag_metrics


# ================================================
# Path Fixtures
# ================================================

@pytest.fixture(scope="session")
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def data_dir(project_root):
    """Return the data directory path."""
    return project_root / "data"


@pytest.fixture(scope="session")
def chroma_db_path(project_root):
    """Return the ChromaDB path."""
    return str(project_root / "chroma_db")


# ================================================
# Golden Dataset Fixture
# ================================================

@pytest.fixture(scope="session")
def golden_dataset(project_root):
    """
    Load the golden dataset for RAG evaluation.

    Expected format:
    [
        {
            "query": "cashier can't void",
            "expected_keywords": ["void", "permission", "employee"],
            "expected_tables": ["tbOrderDetail", "tbEmployee"],
            "min_similarity": 0.70
        },
        ...
    ]

    Returns:
        List of golden dataset entries
    """
    golden_path = project_root / "golden_dataset.json"

    if not golden_path.exists():
        # Return empty list if file doesn't exist yet
        # Tests can skip if dataset is required
        return []

    with open(golden_path, "r") as f:
        dataset = json.load(f)

    return dataset


# ================================================
# Sample Queries Fixture
# ================================================

@pytest.fixture(scope="session")
def sample_queries():
    """
    Common test queries for various scenarios.

    Returns:
        Dict of query categories and examples
    """
    return {
        "printer": [
            "printer not printing",
            "kitchen printer offline",
            "receipt printing twice",
            "printer routing wrong station"
        ],
        "payment": [
            "customer charged twice",
            "card declined but charged",
            "payment not recording on order",
            "batch won't settle"
        ],
        "employee": [
            "employee already clocked in",
            "cashier can't void",
            "PIN not working",
            "employee missing from POS"
        ],
        "order": [
            "order won't close",
            "can't void order",
            "wrong tax calculation",
            "order disappeared"
        ],
        "menu": [
            "item not showing on POS",
            "wrong price displaying",
            "modifier options missing",
            "new item not syncing"
        ],
        "cash": [
            "drawer over short",
            "can't reconcile drawer",
            "drop not recorded",
            "multiple employees same drawer"
        ],
        "edge_cases": [
            "",  # Empty query
            "x",  # Single character
            "help",  # Generic/vague
            "SELECT * FROM tbOrder WHERE OrderNum = 123",  # SQL query itself
            "This is a really long query that goes on and on with lots of details about a complex issue involving multiple systems and components and probably way too much information for a simple search but we should handle it gracefully anyway"  # Very long
        ]
    }


# ================================================
# Configuration Fixtures
# ================================================

@pytest.fixture(scope="session")
def test_config():
    """
    Test configuration values.

    Returns:
        Dict with test configuration
    """
    return {
        "embedding_model": "text-embedding-ada-002",
        "llm_model": "gpt-4o-mini",
        "chunk_size": 2000,
        "chunk_overlap": 200,
        "distance_threshold": 0.40,
        "retrieve_k": 20,
        "return_k": 3,
        "followup_threshold": 0.30,
        "max_followups": 4,
        "app_password": os.getenv("APP_PASSWORD", "escalation2024")
    }


# ================================================
# Mock Data Fixtures
# ================================================

@pytest.fixture
def mock_search_results():
    """
    Mock search results for testing without hitting the database.

    Returns:
        List of mock ChromaDB results
    """
    return [
        {
            "content": "To check employee permissions for voiding: SELECT * FROM tbEmployee WHERE EmployeeNum = ?",
            "metadata": {"source": "sql_reference.md", "category": "employee"},
            "distance": 0.15,
            "similarity_pct": 85.0
        },
        {
            "content": "Check order details: SELECT * FROM tbOrderDetail WHERE OrderNum = ?",
            "metadata": {"source": "sql_reference.md", "category": "order"},
            "distance": 0.25,
            "similarity_pct": 75.0
        },
        {
            "content": "Review employee clock status: SELECT * FROM tbTimeClock WHERE EmployeeNum = ?",
            "metadata": {"source": "sql_reference.md", "category": "employee"},
            "distance": 0.35,
            "similarity_pct": 65.0
        }
    ]


@pytest.fixture
def mock_llm_response():
    """
    Mock LLM response for testing.

    Returns:
        Sample assistant response
    """
    return """Based on the issue you described, here's the SQL query to investigate:

```sql
SELECT EmployeeNum, EmployeeName, SecurityLevel
FROM tbEmployee
WHERE EmployeeNum = ?
```

Look for the SecurityLevel field - cashiers typically need level 5 or higher to void items.
If the level is too low, you'll need to update their permissions in the back office."""


# ================================================
# Streamlit App Fixtures
# ================================================

@pytest.fixture
def fresh_app():
    """
    Create a fresh Streamlit app instance for testing.

    Note: Requires streamlit>=1.18.0 for AppTest

    Returns:
        Streamlit AppTest instance
    """
    try:
        from streamlit.testing.v1 import AppTest

        # Create fresh app instance
        app = AppTest.from_file("app.py")
        return app
    except ImportError:
        pytest.skip("streamlit.testing.v1.AppTest not available (requires Streamlit >=1.18.0)")


@pytest.fixture
def authenticated_app(test_config):
    """
    Create a pre-authenticated Streamlit app instance.

    Returns:
        Authenticated AppTest instance with session state set up
    """
    try:
        from streamlit.testing.v1 import AppTest

        # Create app instance
        app = AppTest.from_file("app.py")

        # Set up authentication in session state
        app.session_state.authenticated = True
        app.session_state.messages = []
        app.session_state.followup_active = False
        app.session_state.original_query = ""
        app.session_state.followup_count = 0
        app.session_state.enriched_context = []
        app.session_state.pending_followup = None
        app.session_state.cached_matches = []

        return app
    except ImportError:
        pytest.skip("streamlit.testing.v1.AppTest not available (requires Streamlit >=1.18.0)")


# ================================================
# RAG Metrics Fixture
# ================================================

@pytest.fixture
def rag_metrics_tracker(request):
    """
    Fixture to track RAG metrics for test reporting.

    Usage in tests:
        def test_search(rag_metrics_tracker):
            results = search(query)
            rag_metrics_tracker.record({
                'similarity': results[0]['similarity_pct'],
                'retrieval_time': 150,
                'num_results': len(results)
            })
    """
    class MetricsTracker:
        def __init__(self, test_item):
            self.test_item = test_item
            self.metrics = {}

        def record(self, metrics: Dict[str, Any]):
            """Record metrics for this test."""
            self.metrics = metrics
            self.test_item.rag_metrics = metrics

        def get(self):
            """Get recorded metrics."""
            return self.metrics

    return MetricsTracker(request.node)


# ================================================
# Database Fixtures
# ================================================

@pytest.fixture(scope="session")
def chroma_collection(chroma_db_path):
    """
    Get the ChromaDB collection for testing.

    Note: This uses the actual database. For isolated tests,
    consider using mock_search_results instead.

    Returns:
        ChromaDB collection instance
    """
    import chromadb
    from chromadb.utils import embedding_functions
    import config

    try:
        openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=config.OPENAI_API_KEY,
            model_name=config.EMBEDDING_MODEL
        )

        client = chromadb.PersistentClient(path=chroma_db_path)
        collection = client.get_collection(
            name=config.COLLECTION_NAME,
            embedding_function=openai_ef
        )

        return collection
    except Exception as e:
        pytest.skip(f"Could not load ChromaDB collection: {e}")


@pytest.fixture(scope="session")
def openai_client():
    """
    Get OpenAI client for testing.

    Returns:
        OpenAI client instance
    """
    from openai import OpenAI
    import config

    if not config.OPENAI_API_KEY:
        pytest.skip("OPENAI_API_KEY not configured")

    return OpenAI(api_key=config.OPENAI_API_KEY)


# ================================================
# Cleanup Fixtures
# ================================================

@pytest.fixture(autouse=True)
def cleanup_test_files(project_root):
    """
    Cleanup any test artifacts after each test.
    """
    yield

    # Clean up test feedback files
    test_feedback = project_root / "feedback_test.json"
    if test_feedback.exists():
        test_feedback.unlink()


# ================================================
# Markers
# ================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (may be slow)"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", "requires_api: marks tests that require OpenAI API access"
    )
    config.addinivalue_line(
        "markers", "requires_db: marks tests that require ChromaDB"
    )
    config.addinivalue_line(
        "markers", "ui: marks tests for Streamlit UI components"
    )
