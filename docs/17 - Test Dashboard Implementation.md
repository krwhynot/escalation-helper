# Test Dashboard Implementation

This document covers test reporting strategies for the Escalation Helper RAG testing suite, with **pytest-html** as the primary recommended approach.

## Overview

Test dashboards provide visual feedback on test results, metrics, and trends. For RAG systems, dashboards should surface:
- Pass/fail rates
- RAG evaluation metrics (faithfulness, context recall, relevancy)
- Query/response samples
- Performance benchmarks

## 1. pytest-html (PRIMARY RECOMMENDATION)

### Why pytest-html?

**Best for Escalation Helper because:**
- No additional infrastructure (generates standalone HTML)
- Easy to integrate with existing pytest suite
- Customizable for RAG-specific metrics
- Works in CI/CD with artifact storage
- Zero setup overhead

### Installation

```bash
pip install pytest-html
```

Add to `requirements.txt`:
```
pytest-html>=4.1.1
```

### Basic Usage

Generate a self-contained HTML report:

```bash
pytest --html=report.html --self-contained-html
```

Options:
- `--html=PATH`: Output path for report
- `--self-contained-html`: Embed CSS/JS inline (single file)
- `--css=PATH`: Custom stylesheet

### Configuration in pytest.ini

Create `/home/krwhynot/projects/escalation-helper/pytest.ini`:

```ini
[pytest]
# Auto-generate HTML reports
addopts = --html=reports/test_report.html --self-contained-html -v

# Test discovery
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Markers for RAG tests
markers =
    rag_eval: RAG evaluation tests with metrics
    integration: Integration tests
    unit: Unit tests
```

Now running `pytest` automatically generates the report:
```bash
pytest  # Creates reports/test_report.html
```

## 2. Customizing Reports for RAG Testing

### Custom Report Title and Metadata

Create `tests/conftest.py`:

```python
import pytest
from datetime import datetime

def pytest_html_report_title(report):
    """Set custom report title"""
    report.title = "Escalation Helper - RAG Test Report"

def pytest_configure(config):
    """Add project metadata to report"""
    config._metadata = {
        'Project': 'Escalation Helper',
        'Test Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'RAG Framework': 'RAGAS',
        'LLM Model': 'GPT-4o-mini',
        'Embedding Model': 'text-embedding-ada-002',
        'Vector DB': 'ChromaDB',
        'Distance Threshold': '0.40 (60% similarity)',
        'Python Version': f"{pytest.__version__}"
    }

def pytest_html_results_summary(prefix, summary, postfix):
    """Add custom summary section"""
    prefix.extend([
        "<div style='background-color:#f0f8ff; padding:15px; border-radius:5px; margin:10px 0;'>",
        "<h3>RAG Testing Suite for SQL Troubleshooting Assistant</h3>",
        "<p><strong>Quality Thresholds:</strong></p>",
        "<ul>",
        "<li>Faithfulness: > 0.85 (answers grounded in context)</li>",
        "<li>Context Recall: > 0.80 (relevant context retrieved)</li>",
        "<li>Answer Relevancy: > 0.85 (response addresses query)</li>",
        "</ul>",
        "</div>"
    ])
```

### Custom CSS (HungerRush Branding)

Create `tests/custom_report.css`:

```css
/* HungerRush Branded Test Report */

body {
    font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
    background-color: #f5f5f5;
}

h1 {
    color: #0E8476;  /* HungerRush teal */
    border-bottom: 3px solid #0E8476;
    padding-bottom: 10px;
}

h2 {
    color: #333;
    border-bottom: 1px solid #ddd;
    padding-bottom: 5px;
}

/* Summary table styling */
.summary__data {
    font-size: 1.3em;
    font-weight: bold;
}

/* Test result colors */
.passed {
    background-color: #d4edda;
    border-left: 4px solid #28a745;
}

.failed {
    background-color: #f8d7da;
    border-left: 4px solid #dc3545;
}

.skipped {
    background-color: #fff3cd;
    border-left: 4px solid #ffc107;
}

.xfailed {
    background-color: #e2e3e5;
    border-left: 4px solid #6c757d;
}

/* Table styling */
table {
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

th {
    background-color: #0E8476;
    color: white;
    padding: 12px;
    text-align: left;
}

td {
    padding: 10px;
    border-bottom: 1px solid #ddd;
}

tr:hover {
    background-color: #f9f9f9;
}

/* Metrics display */
.rag-metrics {
    background-color: #e8f5f3;
    padding: 10px;
    border-radius: 5px;
    margin: 10px 0;
    border-left: 4px solid #0E8476;
}

.rag-metrics strong {
    color: #0E8476;
}

.rag-metrics ul {
    margin: 5px 0;
}

/* Details/summary styling */
details {
    margin: 10px 0;
    padding: 10px;
    background-color: #f9f9f9;
    border-radius: 5px;
}

summary {
    cursor: pointer;
    font-weight: bold;
    color: #0E8476;
}

summary:hover {
    color: #0a6559;
}

pre {
    background-color: #f4f4f4;
    padding: 10px;
    border-radius: 3px;
    overflow-x: auto;
}
```

Update `pytest.ini` to use custom CSS:

```ini
[pytest]
addopts = --html=reports/test_report.html --self-contained-html --css=tests/custom_report.css -v
testpaths = tests
python_files = test_*.py
```

## 3. Adding RAG Metrics to Reports

### Capture and Display Metrics

Extend `tests/conftest.py`:

```python
import pytest
from pytest_html import extras

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Add extra information to test results.
    Captures RAG metrics and query/response data.
    """
    outcome = yield
    report = outcome.get_result()

    # Only process on test call phase (not setup/teardown)
    if report.when != "call":
        return

    # Initialize extras list
    report.extra = getattr(report, 'extra', [])

    # Add RAG metrics if available
    if hasattr(item, 'rag_metrics'):
        metrics = item.rag_metrics

        # Format metrics with color coding
        def format_metric(value, threshold):
            if value is None or value == 'N/A':
                return f"<span style='color:#666;'>N/A</span>"
            color = '#28a745' if value >= threshold else '#dc3545'
            return f"<span style='color:{color}; font-weight:bold;'>{value:.3f}</span>"

        html = f'''
        <div class="rag-metrics">
            <strong>RAG Evaluation Metrics:</strong>
            <table style="margin-top:5px; width:100%; max-width:500px;">
                <tr>
                    <td>Faithfulness:</td>
                    <td>{format_metric(metrics.get('faithfulness'), 0.85)}</td>
                    <td style="color:#666; font-size:0.9em;">(threshold: 0.85)</td>
                </tr>
                <tr>
                    <td>Context Recall:</td>
                    <td>{format_metric(metrics.get('context_recall'), 0.80)}</td>
                    <td style="color:#666; font-size:0.9em;">(threshold: 0.80)</td>
                </tr>
                <tr>
                    <td>Answer Relevancy:</td>
                    <td>{format_metric(metrics.get('relevancy'), 0.85)}</td>
                    <td style="color:#666; font-size:0.9em;">(threshold: 0.85)</td>
                </tr>
                <tr>
                    <td>Context Precision:</td>
                    <td>{format_metric(metrics.get('context_precision'), 0.75)}</td>
                    <td style="color:#666; font-size:0.9em;">(threshold: 0.75)</td>
                </tr>
            </table>
        </div>
        '''
        report.extra.append(extras.html(html))

    # Add query and response details
    if hasattr(item, 'rag_query'):
        query = item.rag_query
        response = getattr(item, 'rag_response', 'N/A')
        contexts = getattr(item, 'rag_contexts', [])

        # Truncate long responses
        response_preview = response[:500] + '...' if len(response) > 500 else response

        # Format contexts
        contexts_html = ''
        if contexts:
            contexts_html = '<h4>Retrieved Contexts:</h4><ol>'
            for ctx in contexts[:3]:  # Show top 3
                ctx_preview = ctx[:200] + '...' if len(ctx) > 200 else ctx
                contexts_html += f'<li><pre>{ctx_preview}</pre></li>'
            contexts_html += '</ol>'

        html = f'''
        <details style="margin-top:10px;">
            <summary>Query & Response Details</summary>
            <div style="padding:10px;">
                <h4>User Query:</h4>
                <pre style="background:#f0f8ff; padding:10px; border-radius:3px;">{query}</pre>

                <h4>Generated Response:</h4>
                <pre style="background:#f0fff0; padding:10px; border-radius:3px;">{response_preview}</pre>

                {contexts_html}
            </div>
        </details>
        '''
        report.extra.append(extras.html(html))

    # Add performance metrics if available
    if hasattr(item, 'performance_metrics'):
        perf = item.performance_metrics
        html = f'''
        <div style="background:#fff3cd; padding:10px; border-radius:5px; margin:10px 0;">
            <strong>Performance:</strong>
            Search: {perf.get('search_time', 'N/A')}ms |
            LLM: {perf.get('llm_time', 'N/A')}ms |
            Total: {perf.get('total_time', 'N/A')}ms
        </div>
        '''
        report.extra.append(extras.html(html))
```

### Using Metrics in Tests

Example test with metrics capture:

```python
import pytest
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    context_recall,
    answer_relevancy,
    context_precision
)
from datasets import Dataset

@pytest.mark.rag_eval
def test_search_quality_cashier_void(request, authenticated_app):
    """
    Test RAG quality for cashier void order query.
    Evaluates faithfulness, recall, and relevancy.
    """
    query = "cashier can't void an order"

    # Run search
    results = search_knowledge_base(query, k=3)
    contexts = [r['text'] for r in results]

    # Generate response
    response = generate_llm_response(query, contexts)

    # Create dataset for RAGAS
    eval_dataset = Dataset.from_dict({
        'question': [query],
        'answer': [response],
        'contexts': [contexts],
        'ground_truth': ["Use SELECT * FROM TransactionLineItem WHERE IsVoided = 1"]
    })

    # Evaluate
    scores = evaluate(
        eval_dataset,
        metrics=[faithfulness, context_recall, answer_relevancy, context_precision]
    )

    # Store metrics for report
    request.node.rag_metrics = {
        'faithfulness': scores['faithfulness'],
        'context_recall': scores['context_recall'],
        'relevancy': scores['answer_relevancy'],
        'context_precision': scores['context_precision']
    }

    # Store query/response for report
    request.node.rag_query = query
    request.node.rag_response = response
    request.node.rag_contexts = contexts

    # Assertions
    assert scores['faithfulness'] > 0.85, f"Faithfulness too low: {scores['faithfulness']}"
    assert scores['context_recall'] > 0.80, f"Context recall too low: {scores['context_recall']}"
    assert scores['answer_relevancy'] > 0.85, f"Answer relevancy too low: {scores['answer_relevancy']}"
```

## 4. Screenshots on Failure

For Streamlit UI tests, capture screenshots when tests fail:

```python
import pytest
from pytest_html import extras
from streamlit.testing.v1 import AppTest
import base64

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Add screenshots on failure for Streamlit tests"""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        # Check if this is a Streamlit test
        if hasattr(item, 'funcargs') and 'authenticated_app' in item.funcargs:
            app = item.funcargs['authenticated_app']

            # Capture app state
            report.extra = getattr(report, 'extra', [])

            # Add session state
            state_html = f'''
            <details>
                <summary>Session State at Failure</summary>
                <pre>{str(app.session_state)}</pre>
            </details>
            '''
            report.extra.append(extras.html(state_html))

            # Add UI component snapshot
            components_html = '<h4>UI Components:</h4><ul>'
            for elem in app.text_input:
                components_html += f'<li>Text Input: {elem.label} = "{elem.value}"</li>'
            for elem in app.button:
                components_html += f'<li>Button: {elem.label}</li>'
            components_html += '</ul>'
            report.extra.append(extras.html(components_html))
```

## 5. Complete conftest.py for Escalation Helper

Full example with all features:

```python
"""
Pytest configuration for Escalation Helper RAG testing.
Includes pytest-html customization, fixtures, and metric capture.
"""

import pytest
from datetime import datetime
from pytest_html import extras
from streamlit.testing.v1 import AppTest
import time

# ============ PYTEST-HTML CUSTOMIZATION ============

def pytest_html_report_title(report):
    """Set custom report title"""
    report.title = "Escalation Helper - RAG Test Report"

def pytest_configure(config):
    """Add project metadata to report"""
    config._metadata = {
        'Project': 'Escalation Helper',
        'Description': 'AI-powered SQL troubleshooting assistant',
        'Test Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'RAG Framework': 'RAGAS',
        'LLM Model': 'GPT-4o-mini',
        'Embedding Model': 'text-embedding-ada-002',
        'Vector DB': 'ChromaDB',
        'Distance Threshold': '0.40 (60% similarity)',
        'Retrieve K': '20',
        'Return K': '3',
        'Python Version': f"{pytest.__version__}"
    }

def pytest_html_results_summary(prefix, summary, postfix):
    """Add custom summary section to report"""
    prefix.extend([
        "<div style='background: linear-gradient(135deg, #e8f5f3 0%, #f0f8ff 100%); "
        "padding:20px; border-radius:8px; margin:15px 0; border-left:5px solid #0E8476;'>",
        "<h3 style='color:#0E8476; margin-top:0;'>RAG Testing Suite Overview</h3>",
        "<p><strong>System:</strong> SQL Troubleshooting Assistant for HungerRush Installer Team</p>",
        "<p><strong>Test Strategy:</strong> Two-stage RAG with semantic search and cross-encoder reranking</p>",
        "<h4 style='color:#333; margin-top:15px;'>Quality Thresholds</h4>",
        "<table style='background:white; border-radius:5px; padding:10px; width:100%; max-width:600px;'>",
        "<tr><td><strong>Faithfulness</strong></td><td>> 0.85</td><td>Answers grounded in context</td></tr>",
        "<tr><td><strong>Context Recall</strong></td><td>> 0.80</td><td>Relevant context retrieved</td></tr>",
        "<tr><td><strong>Answer Relevancy</strong></td><td>> 0.85</td><td>Response addresses query</td></tr>",
        "<tr><td><strong>Context Precision</strong></td><td>> 0.75</td><td>Retrieved context is precise</td></tr>",
        "</table>",
        "</div>"
    ])

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Add extra information to test results.
    Captures RAG metrics, query/response data, and performance metrics.
    """
    outcome = yield
    report = outcome.get_result()

    # Only process on test call phase
    if report.when != "call":
        return

    # Initialize extras list
    report.extra = getattr(report, 'extra', [])

    # Add RAG metrics if available
    if hasattr(item, 'rag_metrics'):
        metrics = item.rag_metrics

        def format_metric(value, threshold):
            """Format metric with color based on threshold"""
            if value is None or value == 'N/A':
                return f"<span style='color:#666;'>N/A</span>"
            color = '#28a745' if value >= threshold else '#dc3545'
            icon = '✓' if value >= threshold else '✗'
            return f"{icon} <span style='color:{color}; font-weight:bold;'>{value:.3f}</span>"

        html = f'''
        <div class="rag-metrics" style="background:#e8f5f3; padding:15px; border-radius:5px;
             margin:10px 0; border-left:4px solid #0E8476;">
            <strong style="color:#0E8476; font-size:1.1em;">RAG Evaluation Metrics</strong>
            <table style="margin-top:10px; width:100%; max-width:600px; background:white;
                   border-radius:5px; padding:5px;">
                <tr>
                    <td style="padding:8px;"><strong>Faithfulness</strong></td>
                    <td style="padding:8px;">{format_metric(metrics.get('faithfulness'), 0.85)}</td>
                    <td style="padding:8px; color:#666; font-size:0.9em;">threshold: ≥ 0.85</td>
                </tr>
                <tr>
                    <td style="padding:8px;"><strong>Context Recall</strong></td>
                    <td style="padding:8px;">{format_metric(metrics.get('context_recall'), 0.80)}</td>
                    <td style="padding:8px; color:#666; font-size:0.9em;">threshold: ≥ 0.80</td>
                </tr>
                <tr>
                    <td style="padding:8px;"><strong>Answer Relevancy</strong></td>
                    <td style="padding:8px;">{format_metric(metrics.get('relevancy'), 0.85)}</td>
                    <td style="padding:8px; color:#666; font-size:0.9em;">threshold: ≥ 0.85</td>
                </tr>
                <tr>
                    <td style="padding:8px;"><strong>Context Precision</strong></td>
                    <td style="padding:8px;">{format_metric(metrics.get('context_precision'), 0.75)}</td>
                    <td style="padding:8px; color:#666; font-size:0.9em;">threshold: ≥ 0.75</td>
                </tr>
            </table>
        </div>
        '''
        report.extra.append(extras.html(html))

    # Add query and response details
    if hasattr(item, 'rag_query'):
        query = item.rag_query
        response = getattr(item, 'rag_response', 'N/A')
        contexts = getattr(item, 'rag_contexts', [])

        # Truncate long responses for preview
        response_preview = response[:500] + '...' if len(response) > 500 else response

        # Format retrieved contexts
        contexts_html = ''
        if contexts:
            contexts_html = '<h4 style="color:#333; margin-top:15px;">Retrieved Contexts (Top 3):</h4><ol>'
            for i, ctx in enumerate(contexts[:3], 1):
                ctx_preview = ctx[:300] + '...' if len(ctx) > 300 else ctx
                contexts_html += f'''
                <li style="margin:10px 0;">
                    <pre style="background:#f9f9f9; padding:10px; border-radius:3px;
                         font-size:0.9em; overflow-x:auto;">{ctx_preview}</pre>
                </li>
                '''
            contexts_html += '</ol>'

        html = f'''
        <details style="margin-top:10px; background:#f9f9f9; padding:15px; border-radius:5px;">
            <summary style="cursor:pointer; font-weight:bold; color:#0E8476; font-size:1.05em;">
                📋 Query & Response Details
            </summary>
            <div style="padding:10px; margin-top:10px;">
                <h4 style="color:#333;">User Query:</h4>
                <pre style="background:#f0f8ff; padding:12px; border-radius:5px;
                     border-left:3px solid #0E8476;">{query}</pre>

                <h4 style="color:#333; margin-top:15px;">Generated Response:</h4>
                <pre style="background:#f0fff0; padding:12px; border-radius:5px;
                     border-left:3px solid #28a745; overflow-x:auto;">{response_preview}</pre>

                {contexts_html}
            </div>
        </details>
        '''
        report.extra.append(extras.html(html))

    # Add performance metrics if available
    if hasattr(item, 'performance_metrics'):
        perf = item.performance_metrics
        total = perf.get('total_time', 0)

        # Color code based on performance
        perf_color = '#28a745' if total < 2000 else '#ffc107' if total < 5000 else '#dc3545'

        html = f'''
        <div style="background:#fff3cd; padding:12px; border-radius:5px; margin:10px 0;
             border-left:4px solid {perf_color};">
            <strong>⚡ Performance Metrics:</strong><br>
            <div style="margin-top:5px; font-family:monospace;">
                Search Time: <strong>{perf.get('search_time', 'N/A')}ms</strong> |
                LLM Generation: <strong>{perf.get('llm_time', 'N/A')}ms</strong> |
                Total: <strong style="color:{perf_color};">{total}ms</strong>
            </div>
        </div>
        '''
        report.extra.append(extras.html(html))

    # Add failure details for Streamlit tests
    if report.failed and hasattr(item, 'funcargs') and 'authenticated_app' in item.funcargs:
        app = item.funcargs['authenticated_app']

        state_html = f'''
        <details style="margin-top:10px; background:#f8d7da; padding:15px; border-radius:5px;">
            <summary style="cursor:pointer; font-weight:bold; color:#721c24;">
                🔍 Streamlit Session State at Failure
            </summary>
            <pre style="background:#fff; padding:10px; margin-top:10px; border-radius:3px;
                 overflow-x:auto;">{str(dict(app.session_state))}</pre>
        </details>
        '''
        report.extra.append(extras.html(state_html))

# ============ TEST FIXTURES ============

@pytest.fixture(scope="session")
def test_start_time():
    """Record test session start time"""
    return time.time()

@pytest.fixture
def authenticated_app():
    """
    Pre-authenticated Streamlit app instance.
    Bypasses password entry for testing.
    """
    at = AppTest.from_file("app.py")

    # Mock secrets
    at.secrets["OPENAI_API_KEY"] = "test-key-placeholder"
    at.secrets["APP_PASSWORD"] = "escalation2024"

    # Set authenticated state
    at.session_state.authenticated = True

    at.run()
    return at

@pytest.fixture
def sample_queries():
    """
    Sample test queries covering main troubleshooting categories.
    """
    return {
        'cashier': [
            "cashier can't void an order",
            "cashier unable to apply discount",
            "cashier can't clock out"
        ],
        'printer': [
            "printer not printing receipts",
            "kitchen printer offline",
            "receipt shows garbled text"
        ],
        'payment': [
            "credit card payment failed",
            "gift card won't process",
            "cash drawer won't open"
        ],
        'employee': [
            "employee can't clock in",
            "employee missing from list",
            "employee permissions not working"
        ],
        'menu': [
            "menu item not appearing",
            "price wrong on receipt",
            "modifier not working"
        ]
    }

@pytest.fixture
def performance_tracker():
    """
    Context manager for tracking operation performance.

    Usage:
        with performance_tracker() as tracker:
            # do work
            pass

        print(tracker.elapsed_ms)
    """
    class PerformanceTracker:
        def __init__(self):
            self.start = None
            self.end = None

        def __enter__(self):
            self.start = time.time()
            return self

        def __exit__(self, *args):
            self.end = time.time()

        @property
        def elapsed_ms(self):
            if self.start and self.end:
                return int((self.end - self.start) * 1000)
            return None

    return PerformanceTracker

@pytest.fixture
def ground_truths():
    """
    Ground truth SQL queries for evaluation.
    Maps user queries to expected SQL patterns.
    """
    return {
        "cashier can't void an order": "SELECT * FROM TransactionLineItem WHERE IsVoided = 1",
        "printer not printing receipts": "SELECT * FROM Printer WHERE IsEnabled = 1",
        "employee can't clock in": "SELECT * FROM Employee WHERE IsActive = 1",
        "credit card payment failed": "SELECT * FROM Payment WHERE PaymentType = 'CreditCard'",
    }
```

## 6. Running and Viewing Reports

### Generate Report

```bash
# Basic report generation
pytest --html=reports/test_report.html --self-contained-html

# With verbose output
pytest --html=reports/test_report.html --self-contained-html -v

# Run specific test markers
pytest --html=reports/test_report.html --self-contained-html -m rag_eval

# Run with custom CSS
pytest --html=reports/test_report.html --self-contained-html --css=tests/custom_report.css
```

### View Report

```bash
# Linux
xdg-open reports/test_report.html

# macOS
open reports/test_report.html

# Windows
start reports/test_report.html

# Windows (PowerShell)
Invoke-Item reports\test_report.html
```

### Organize Reports by Date

```bash
# Generate timestamped report
pytest --html=reports/test_report_$(date +%Y%m%d_%H%M%S).html --self-contained-html

# Python script for timestamped reports
python -c "import datetime; import os; os.system(f'pytest --html=reports/test_report_{datetime.datetime.now().strftime(\"%Y%m%d_%H%M%S\")}.html --self-contained-html')"
```

## 7. CI/CD Integration

### GitHub Actions

`.github/workflows/test.yml`:

```yaml
name: RAG Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.12'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run tests with HTML report
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      run: |
        mkdir -p reports
        pytest --html=reports/test_report.html --self-contained-html -v

    - name: Upload test report
      uses: actions/upload-artifact@v4
      if: always()  # Upload even if tests fail
      with:
        name: test-report-${{ github.run_number }}
        path: reports/test_report.html
        retention-days: 30

    - name: Comment PR with report link
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v7
      with:
        script: |
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: '📊 Test report available in [workflow artifacts](https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }})'
          })
```

### GitLab CI

`.gitlab-ci.yml`:

```yaml
stages:
  - test

rag_tests:
  stage: test
  image: python:3.12

  before_script:
    - pip install -r requirements.txt

  script:
    - mkdir -p reports
    - pytest --html=reports/test_report.html --self-contained-html -v

  artifacts:
    when: always
    paths:
      - reports/test_report.html
    expire_in: 30 days

  only:
    - main
    - develop
    - merge_requests
```

### Jenkins

```groovy
pipeline {
    agent any

    stages {
        stage('Setup') {
            steps {
                sh 'python -m venv venv'
                sh '. venv/bin/activate && pip install -r requirements.txt'
            }
        }

        stage('Test') {
            steps {
                sh '. venv/bin/activate && pytest --html=reports/test_report.html --self-contained-html -v'
            }
        }
    }

    post {
        always {
            publishHTML(target: [
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'reports',
                reportFiles: 'test_report.html',
                reportName: 'RAG Test Report'
            ])
        }
    }
}
```

## 8. Alternative Solutions

### Option A: Allure Framework

**When to use:** Need historical trends, rich visualizations, and multi-project dashboards.

**Installation:**
```bash
pip install allure-pytest

# Also need Allure CLI
# macOS
brew install allure

# Linux
curl -o allure-2.25.0.tgz -L https://github.com/allure-framework/allure2/releases/download/2.25.0/allure-2.25.0.tgz
tar -zxvf allure-2.25.0.tgz
sudo mv allure-2.25.0 /opt/allure
export PATH=$PATH:/opt/allure/bin
```

**Usage:**
```bash
# Generate results
pytest --alluredir=allure-results

# Serve interactive report
allure serve allure-results

# Generate static HTML
allure generate allure-results --clean -o allure-report
```

**Pros:**
- Beautiful interactive UI
- Historical trends and comparisons
- Categorization and suites
- Screenshot/attachment support

**Cons:**
- Requires Allure CLI installation
- More complex setup
- Not self-contained (needs web server)

### Option B: Custom Streamlit Dashboard

**When to use:** Want real-time monitoring, live updates, or integration with app UI.

**Example implementation:**

```python
# tests/dashboard.py
import streamlit as st
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="RAG Test Dashboard", layout="wide")

st.title("Escalation Helper - RAG Test Dashboard")

# Load test results (from JSON export)
results_dir = Path("reports/json")
result_files = sorted(results_dir.glob("test_*.json"), reverse=True)

if not result_files:
    st.warning("No test results found. Run tests with JSON export first.")
    st.stop()

# Sidebar: Select test run
selected_file = st.sidebar.selectbox(
    "Select Test Run",
    result_files,
    format_func=lambda x: x.stem
)

# Load results
with open(selected_file) as f:
    results = json.load(f)

# Metrics overview
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Tests", results['summary']['total'])
with col2:
    st.metric("Passed", results['summary']['passed'], delta=f"+{results['summary']['passed']}")
with col3:
    st.metric("Failed", results['summary']['failed'], delta=f"-{results['summary']['failed']}" if results['summary']['failed'] > 0 else 0)
with col4:
    pass_rate = (results['summary']['passed'] / results['summary']['total']) * 100
    st.metric("Pass Rate", f"{pass_rate:.1f}%")

# RAG Metrics Trends
st.header("RAG Metrics Trends")

metrics_data = []
for test in results['tests']:
    if 'rag_metrics' in test:
        metrics_data.append({
            'test': test['name'],
            'faithfulness': test['rag_metrics']['faithfulness'],
            'context_recall': test['rag_metrics']['context_recall'],
            'relevancy': test['rag_metrics']['relevancy']
        })

if metrics_data:
    df = pd.DataFrame(metrics_data)
    st.line_chart(df.set_index('test'))

# Test details
st.header("Test Details")
for test in results['tests']:
    with st.expander(f"{'✅' if test['passed'] else '❌'} {test['name']}"):
        if 'rag_query' in test:
            st.subheader("Query")
            st.code(test['rag_query'])

            st.subheader("Response")
            st.text_area("", test['rag_response'], height=150)

        if 'rag_metrics' in test:
            st.subheader("Metrics")
            metrics_df = pd.DataFrame([test['rag_metrics']])
            st.dataframe(metrics_df)
```

**Run dashboard:**
```bash
streamlit run tests/dashboard.py
```

**Pros:**
- Integrated with Streamlit stack
- Real-time updates possible
- Custom visualizations
- Can share with team via URL

**Cons:**
- Requires running Streamlit server
- More maintenance overhead
- Need to export pytest results to JSON

### Option C: pytest-json-report

**When to use:** Need machine-readable results for custom processing.

```bash
pip install pytest-json-report

pytest --json-report --json-report-file=reports/test_results.json
```

Combine with pytest-html for both human and machine-readable outputs:

```bash
pytest --html=reports/test_report.html --self-contained-html --json-report --json-report-file=reports/test_results.json
```

## 9. Recommendation for Escalation Helper

**Phase 1 (Now): Use pytest-html**
- Simplest setup, no infrastructure
- Covers all current needs
- Easy to customize for RAG metrics
- Works in CI/CD with artifact storage

**Phase 2 (If needed): Add Allure**
- When you need historical comparisons
- If multiple people running tests
- When trend analysis becomes important

**Phase 3 (Advanced): Custom Streamlit Dashboard**
- For real-time monitoring
- If you want live test execution tracking
- When integration with main app UI is valuable

## 10. Quick Start Checklist

- [ ] Install pytest-html: `pip install pytest-html`
- [ ] Create `pytest.ini` with HTML generation settings
- [ ] Create `tests/conftest.py` with customizations
- [ ] (Optional) Create `tests/custom_report.css` for branding
- [ ] Add RAG metric capture to tests using `request.node`
- [ ] Run tests: `pytest`
- [ ] Open report: `xdg-open reports/test_report.html`
- [ ] Add to `.gitignore`: `reports/`
- [ ] Configure CI/CD to upload reports as artifacts

## Example Output

After following this guide, your test report will show:

1. **Header**: HungerRush branded with teal accent
2. **Metadata**: Project info, models, thresholds
3. **Summary**: Total tests, pass/fail counts, pass rate
4. **Overview**: RAG testing strategy and quality thresholds
5. **Test Results Table**:
   - Pass/fail status with color coding
   - Test name and duration
   - Expandable RAG metrics (faithfulness, recall, relevancy)
   - Expandable query/response details
   - Performance metrics
6. **Failure Details**: Session state and error traces

All in a single, self-contained HTML file ready to share or archive.
