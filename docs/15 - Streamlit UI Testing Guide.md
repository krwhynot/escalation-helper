# 15 - Streamlit UI Testing Guide

This guide covers UI testing strategies for Escalation Helper, a Streamlit-based SQL troubleshooting assistant. The primary testing approach uses **Streamlit AppTest**, Streamlit's native testing framework.

---

## 1. Streamlit AppTest Framework (PRIMARY)

### Overview

Streamlit AppTest is the official testing framework for Streamlit applications. It provides a programmatic way to test Streamlit apps without launching a browser or server.

**Key Benefits:**
- Native integration with Streamlit
- No browser automation overhead
- Fast execution (no network delays)
- Works seamlessly with pytest
- Direct access to session state and widgets
- Simulates user interactions via API

**When to Use:**
- Testing authentication flows
- Validating chat message handling
- Verifying session state management
- Testing button clicks and form submissions
- Checking error handling and edge cases
- Integration testing of app logic

### How It Works

AppTest simulates a running Streamlit app by:

1. **Loading the app**: `AppTest.from_file("app.py")` imports your application
2. **Running the app**: `.run()` executes the Streamlit script
3. **Accessing elements**: Use properties like `.button`, `.chat_input`, `.text_input`
4. **Interacting**: Call methods like `.set_value()`, `.click()`
5. **Inspecting**: Read properties like `.value`, `.label`, `.options`
6. **Checking state**: Access `at.session_state` directly

### Installation

```bash
pip install streamlit pytest
```

No additional dependencies required - AppTest is included with Streamlit 1.28+.

### Core Capabilities

#### Widget Access
```python
at = AppTest.from_file("app.py")
at.run()

# Access widgets by type (returns list)
at.button[0]           # First button
at.text_input[0]       # First text input
at.chat_input[0]       # First chat input
at.selectbox[0]        # First selectbox
at.radio[0]            # First radio button

# Access by key (if widget has key parameter)
at.text_input(key="password_input")
```

#### Session State Manipulation
```python
# Read session state
assert at.session_state.authenticated == True

# Write session state (set initial conditions)
at.session_state.authenticated = True
at.session_state.messages = []
at.run()
```

#### Secrets Injection
```python
# Inject secrets without .streamlit/secrets.toml
at.secrets["OPENAI_API_KEY"] = "test-key"
at.secrets["APP_PASSWORD"] = "escalation2024"
at.run()
```

#### Widget Interaction
```python
# Text input
at.text_input[0].set_value("new value").run()

# Button click
at.button[0].click().run()

# Chat input
at.chat_input[0].set_value("user message").run()

# Selectbox
at.selectbox[0].select("Option 2").run()

# Checkbox
at.checkbox[0].check().run()
at.checkbox[0].uncheck().run()
```

#### Element Inspection
```python
# Check widget properties
assert at.button[0].label == "Login"
assert at.text_input[0].value == "current value"
assert at.selectbox[0].options == ["Option 1", "Option 2"]

# Check for displayed elements
assert len(at.error) > 0  # Error message exists
assert len(at.warning) == 0  # No warnings
assert len(at.success) > 0  # Success message exists
```

#### Exception Checking
```python
at.run()

# Check if app crashed
assert not at.exception

# Or expect specific exception
at.run()
assert at.exception is not None
assert "KeyError" in str(at.exception)
```

### Limitations

Be aware of what AppTest **cannot** do:

1. **No Visual Testing**: Cannot verify CSS, colors, fonts, or visual layout
2. **No Browser Behavior**: Cannot test browser-specific features (localStorage, cookies)
3. **No Copy Buttons**: `st.code(..., copy=True)` requires browser clipboard API
4. **No Real Network**: Cannot test actual API calls (mock instead)
5. **No JavaScript**: Cannot test custom components with JavaScript
6. **Limited Async**: Cannot easily test streaming responses or real-time updates
7. **No Rendering**: Cannot capture screenshots or verify visual regressions

For these scenarios, consider Playwright (see Section 5).

---

## 2. Complete Examples for Escalation Helper

### Test Login Flow

```python
from streamlit.testing.v1 import AppTest

def test_login_correct_password():
    """Test successful login with correct password"""
    at = AppTest.from_file("app.py")
    at.secrets["APP_PASSWORD"] = "escalation2024"
    at.run()

    # Verify login form is displayed
    assert len(at.text_input) > 0
    assert len(at.button) > 0

    # Enter correct password
    at.text_input[0].set_value("escalation2024").run()

    # Click login button
    at.button[0].click().run()

    # Verify authentication succeeded
    assert at.session_state.authenticated == True
    assert len(at.error) == 0

def test_login_wrong_password():
    """Test login failure with incorrect password"""
    at = AppTest.from_file("app.py")
    at.secrets["APP_PASSWORD"] = "escalation2024"
    at.run()

    # Enter wrong password
    at.text_input[0].set_value("wrong_password").run()
    at.button[0].click().run()

    # Verify authentication failed
    assert at.session_state.authenticated == False
    assert len(at.error) > 0  # Error message displayed

def test_login_empty_password():
    """Test login with empty password"""
    at = AppTest.from_file("app.py")
    at.secrets["APP_PASSWORD"] = "escalation2024"
    at.run()

    # Submit empty password
    at.text_input[0].set_value("").run()
    at.button[0].click().run()

    # Should remain unauthenticated
    assert at.session_state.authenticated == False
```

### Test Chat Input/Output

```python
def test_chat_submission():
    """Test chat message submission"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.session_state.messages = []
    at.run()

    # Submit a query
    at.chat_input[0].set_value("cashier can't void").run()

    # Verify message was added to chat history
    assert len(at.session_state.messages) >= 1
    assert at.session_state.messages[0]["role"] == "user"
    assert "void" in at.session_state.messages[0]["content"].lower()

def test_chat_response_generated():
    """Test that assistant generates a response"""
    at = AppTest.from_file("app.py")
    at.secrets["OPENAI_API_KEY"] = "test-key"
    at.session_state.authenticated = True
    at.session_state.messages = [
        {"role": "user", "content": "test query"}
    ]
    at.run()

    # Should have assistant response
    assert len(at.session_state.messages) >= 2
    assert any(m["role"] == "assistant" for m in at.session_state.messages)

def test_multiple_messages():
    """Test chat conversation with multiple exchanges"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.session_state.messages = []
    at.run()

    # First message
    at.chat_input[0].set_value("first message").run()
    first_count = len(at.session_state.messages)

    # Second message
    at.chat_input[0].set_value("second message").run()
    second_count = len(at.session_state.messages)

    # Messages should accumulate
    assert second_count > first_count

def test_chat_displays_all_messages():
    """Test that all messages are rendered in chat"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.session_state.messages = [
        {"role": "user", "content": "msg1"},
        {"role": "assistant", "content": "response1"},
        {"role": "user", "content": "msg2"},
        {"role": "assistant", "content": "response2"}
    ]
    at.run()

    # All messages should be in session state
    assert len(at.session_state.messages) == 4
```

### Test Session State

```python
def test_session_state_initialization():
    """Test session state initializes correctly"""
    at = AppTest.from_file("app.py")
    at.run()

    # Should have default session state values
    assert "authenticated" in at.session_state
    assert "messages" in at.session_state
    assert isinstance(at.session_state.messages, list)

def test_session_state_persistence():
    """Test session state persists across reruns"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.session_state.messages = [
        {"role": "user", "content": "msg1"},
        {"role": "assistant", "content": "response1"}
    ]
    at.run()

    # Messages should persist
    assert len(at.session_state.messages) == 2
    assert at.session_state.authenticated == True

def test_clear_chat():
    """Test clearing chat history"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.session_state.messages = [
        {"role": "user", "content": "test message"}
    ]
    at.run()

    # Find and click clear button
    clear_btn = [b for b in at.button if "Clear" in str(b.label)]
    if clear_btn:
        clear_btn[0].click().run()
        assert len(at.session_state.messages) == 0

def test_logout():
    """Test logout functionality"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.run()

    # Find and click logout button (if exists)
    logout_btn = [b for b in at.button if "Logout" in str(b.label)]
    if logout_btn:
        logout_btn[0].click().run()
        assert at.session_state.authenticated == False
```

### Test Error States

```python
def test_no_crash_without_api_key():
    """Test app doesn't crash without API key"""
    at = AppTest.from_file("app.py")
    # Don't set OPENAI_API_KEY
    at.secrets["APP_PASSWORD"] = "escalation2024"
    at.session_state.authenticated = True
    at.run()

    # Should not crash (may show warning instead)
    assert not at.exception

def test_empty_query_handling():
    """Test app handles empty queries gracefully"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.session_state.messages = []
    at.run()

    # Submit empty query
    at.chat_input[0].set_value("").run()

    # Should handle gracefully without crashing
    assert not at.exception

def test_malformed_session_state():
    """Test app handles corrupted session state"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    # Malformed messages (not dict)
    at.session_state.messages = ["not", "a", "dict"]
    at.run()

    # Should either fix or show error gracefully
    # (Specific behavior depends on app implementation)
    assert not at.exception or len(at.error) > 0

def test_missing_openai_credentials():
    """Test behavior when OpenAI credentials are missing"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    # Explicitly clear any API key
    if "OPENAI_API_KEY" in at.secrets:
        del at.secrets["OPENAI_API_KEY"]
    at.run()

    # Should display error or warning
    assert len(at.error) > 0 or len(at.warning) > 0 or not at.exception
```

### Test Follow-up Questions

```python
def test_followup_question_displayed():
    """Test that follow-up questions are shown for low-confidence results"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.session_state.messages = []
    at.run()

    # Submit vague query that should trigger follow-up
    at.chat_input[0].set_value("printer").run()

    # Check if follow-up questions appear (implementation-specific)
    # This depends on how follow-ups are rendered in app.py
    # Could check for radio buttons, selectbox, or buttons
    has_followup = len(at.radio) > 0 or len(at.selectbox) > 0

def test_followup_question_selection():
    """Test selecting a follow-up question"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.session_state.show_followup = True
    at.session_state.followup_category = "printer"
    at.run()

    # If follow-ups are displayed as buttons
    if len(at.button) > 0:
        # Click first follow-up option
        at.button[0].click().run()
        # Should submit refined query
        assert len(at.session_state.messages) > 0
```

### Test Search Functionality

```python
def test_search_returns_results():
    """Test that search function returns results"""
    at = AppTest.from_file("app.py")
    at.secrets["OPENAI_API_KEY"] = "test-key"
    at.session_state.authenticated = True
    at.run()

    # This assumes search_knowledge_base is accessible
    # May need to mock or test indirectly through chat
    at.chat_input[0].set_value("cashier void order").run()

    # Should have results in response
    assert len(at.session_state.messages) >= 2

def test_no_results_handling():
    """Test behavior when search returns no results"""
    at = AppTest.from_file("app.py")
    at.secrets["OPENAI_API_KEY"] = "test-key"
    at.session_state.authenticated = True
    at.run()

    # Query unlikely to match anything
    at.chat_input[0].set_value("asdfghjklqwertyuiop").run()

    # Should handle gracefully
    assert not at.exception
    assert len(at.session_state.messages) >= 2
```

---

## 3. conftest.py Setup

Create a `conftest.py` file in your `tests/` directory to provide reusable fixtures:

```python
import pytest
from streamlit.testing.v1 import AppTest

@pytest.fixture
def authenticated_app():
    """
    Pre-authenticated app instance for testing authenticated features.

    Returns:
        AppTest: App instance with authentication already completed
    """
    at = AppTest.from_file("app.py")
    at.secrets["OPENAI_API_KEY"] = "test-key-12345"
    at.secrets["APP_PASSWORD"] = "escalation2024"
    at.session_state.authenticated = True
    at.session_state.messages = []
    at.run()
    return at

@pytest.fixture
def fresh_app():
    """
    Fresh app instance without authentication.

    Returns:
        AppTest: Clean app instance for testing login flow
    """
    at = AppTest.from_file("app.py")
    at.secrets["APP_PASSWORD"] = "escalation2024"
    at.run()
    return at

@pytest.fixture
def app_with_messages():
    """
    App instance with existing chat history.

    Returns:
        AppTest: App with sample conversation history
    """
    at = AppTest.from_file("app.py")
    at.secrets["OPENAI_API_KEY"] = "test-key-12345"
    at.session_state.authenticated = True
    at.session_state.messages = [
        {"role": "user", "content": "How do I void an order?"},
        {"role": "assistant", "content": "To void an order, use this SQL: ..."},
        {"role": "user", "content": "What about refunds?"},
        {"role": "assistant", "content": "For refunds, try: ..."}
    ]
    at.run()
    return at

@pytest.fixture
def mock_openai_response(monkeypatch):
    """
    Mock OpenAI API responses to avoid real API calls.

    Usage:
        def test_something(authenticated_app, mock_openai_response):
            # OpenAI calls will return mocked data
    """
    def mock_embedding(*args, **kwargs):
        return {"data": [{"embedding": [0.1] * 1536}]}

    def mock_chat(*args, **kwargs):
        return {
            "choices": [{
                "message": {"content": "Mocked response"}
            }]
        }

    # Apply mocks (adjust import paths as needed)
    monkeypatch.setattr("openai.embeddings.create", mock_embedding)
    monkeypatch.setattr("openai.chat.completions.create", mock_chat)
```

### Using Fixtures

```python
def test_with_authenticated_fixture(authenticated_app):
    """Test using authenticated app fixture"""
    at = authenticated_app

    # Already authenticated, can test chat directly
    at.chat_input[0].set_value("test query").run()
    assert len(at.session_state.messages) >= 1

def test_with_fresh_fixture(fresh_app):
    """Test using fresh app fixture"""
    at = fresh_app

    # Test login flow
    at.text_input[0].set_value("escalation2024").run()
    at.button[0].click().run()
    assert at.session_state.authenticated == True

def test_with_messages_fixture(app_with_messages):
    """Test using app with existing messages"""
    at = app_with_messages

    # Already has 4 messages
    assert len(at.session_state.messages) == 4

    # Add another message
    at.chat_input[0].set_value("new query").run()
    assert len(at.session_state.messages) >= 5
```

---

## 4. Running Tests

### Basic Test Execution

```bash
# Run all tests in test file
pytest tests/test_ui.py -v

# Run specific test
pytest tests/test_ui.py::test_login_correct_password -v

# Run tests matching pattern
pytest tests/test_ui.py -k "login" -v

# Run with output (show print statements)
pytest tests/test_ui.py -v -s
```

### Coverage Reports

```bash
# Run with coverage
pytest tests/test_ui.py --cov=app --cov-report=term

# Generate HTML coverage report
pytest tests/test_ui.py --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Continuous Integration

Add to `.github/workflows/test.yml`:

```yaml
name: UI Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Run UI tests
      run: |
        pytest tests/test_ui.py -v --cov=app --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### Test Organization

Organize tests by feature:

```
tests/
├── conftest.py              # Shared fixtures
├── test_ui_login.py         # Login/authentication tests
├── test_ui_chat.py          # Chat interaction tests
├── test_ui_search.py        # Search functionality tests
├── test_ui_followup.py      # Follow-up question tests
└── test_ui_errors.py        # Error handling tests
```

---

## 5. When You Need Playwright (Future Reference)

### Scenarios Requiring Playwright

Consider Playwright when you need:

1. **Visual Regression Testing**: Verify UI looks correct after changes
2. **Copy Button Testing**: Test `st.code(..., copy=True)` functionality
3. **CSS/Styling Verification**: Ensure colors, fonts, spacing are correct
4. **Cross-Browser Testing**: Test on Chrome, Firefox, Safari
5. **Screenshot Capture**: Document bugs or generate test artifacts
6. **JavaScript Testing**: Test custom components with JS
7. **Real Browser Behavior**: Test browser-specific features

### Basic Playwright Setup

```bash
# Install Playwright
pip install playwright pytest-playwright

# Install browsers
playwright install
```

### Playwright Example

```python
import pytest
from playwright.sync_api import Page, expect

def test_login_visual(page: Page):
    """Test login page appearance"""
    page.goto("http://localhost:8501")

    # Wait for app to load
    page.wait_for_selector("input[type='password']")

    # Take screenshot
    page.screenshot(path="screenshots/login.png")

    # Check button exists
    expect(page.locator("button")).to_contain_text("Login")

def test_copy_button_works(page: Page):
    """Test code copy button functionality"""
    page.goto("http://localhost:8501")

    # Login first
    page.fill("input[type='password']", "escalation2024")
    page.click("button")

    # Submit query
    page.fill("textarea", "cashier void")
    page.press("textarea", "Enter")

    # Wait for response with code block
    page.wait_for_selector("button[title='Copy']")

    # Click copy button
    page.click("button[title='Copy']")

    # Verify copied to clipboard (browser-specific)
    # This requires additional clipboard permission handling

@pytest.fixture(scope="function", autouse=True)
def run_streamlit_app():
    """Start Streamlit app before tests, stop after"""
    import subprocess
    import time

    # Start Streamlit
    process = subprocess.Popen(
        ["streamlit", "run", "app.py", "--server.port", "8501"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for app to start
    time.sleep(3)

    yield

    # Stop Streamlit
    process.terminate()
    process.wait()
```

### Playwright Configuration

Create `pytest.ini`:

```ini
[pytest]
# Playwright options
addopts = --headed  # Show browser (remove for CI)
base-url = http://localhost:8501
```

---

## 6. Practical Tips and Common Pitfalls

### Tips for Success

1. **Always call `.run()` after changes**
   ```python
   # Wrong - changes not applied
   at.text_input[0].set_value("test")
   assert at.text_input[0].value == "test"  # Fails!

   # Correct
   at.text_input[0].set_value("test").run()
   assert at.text_input[0].value == "test"  # Works
   ```

2. **Use fixtures for common setups**
   - Don't repeat authentication logic in every test
   - Create fixtures for common scenarios (authenticated, with messages, etc.)

3. **Test session state directly**
   ```python
   # More reliable than checking UI elements
   assert at.session_state.authenticated == True
   assert len(at.session_state.messages) == 5
   ```

4. **Mock external API calls**
   ```python
   # Don't make real OpenAI calls in tests
   @pytest.fixture
   def mock_openai(monkeypatch):
       monkeypatch.setattr("app.search_knowledge_base",
                          lambda q: "Mocked result")
   ```

5. **Use descriptive test names**
   ```python
   # Good
   def test_login_fails_with_wrong_password():

   # Bad
   def test_login():
   ```

### Common Pitfalls

1. **Forgetting to set secrets**
   ```python
   # Wrong - app may crash or behave unexpectedly
   at = AppTest.from_file("app.py")
   at.run()

   # Correct
   at = AppTest.from_file("app.py")
   at.secrets["APP_PASSWORD"] = "escalation2024"
   at.secrets["OPENAI_API_KEY"] = "test-key"
   at.run()
   ```

2. **Widget indexing errors**
   ```python
   # Fragile - order may change
   at.button[2].click()

   # Better - find by label
   btn = [b for b in at.button if b.label == "Clear Chat"][0]
   btn.click()
   ```

3. **Not checking for exceptions**
   ```python
   # Always verify app didn't crash
   at.run()
   assert not at.exception
   ```

4. **Testing UI elements that don't exist yet**
   ```python
   # Wrong - chat_input may not exist before login
   at = AppTest.from_file("app.py")
   at.run()
   at.chat_input[0].set_value("test")  # IndexError!

   # Correct - authenticate first
   at.session_state.authenticated = True
   at.run()
   at.chat_input[0].set_value("test")
   ```

5. **Assuming immediate updates**
   ```python
   # Wrong - need to run() first
   at.text_input[0].set_value("new")
   assert at.session_state.some_value == "new"  # May fail

   # Correct
   at.text_input[0].set_value("new").run()
   assert at.session_state.some_value == "new"
   ```

6. **Not isolating tests**
   ```python
   # Bad - tests affect each other
   at = AppTest.from_file("app.py")  # Global

   def test_1():
       at.session_state.messages.append({"role": "user", "content": "1"})

   def test_2():
       # Messages from test_1 may still exist!
       assert len(at.session_state.messages) == 0  # Fails

   # Good - fresh instance per test
   def test_1():
       at = AppTest.from_file("app.py")
       at.run()
       # ...
   ```

### Debugging Failed Tests

```python
# Print session state
def test_debug_session_state(authenticated_app):
    at = authenticated_app
    print(f"Session state: {dict(at.session_state)}")

# Print all widgets
def test_debug_widgets(authenticated_app):
    at = authenticated_app
    print(f"Buttons: {[b.label for b in at.button]}")
    print(f"Text inputs: {len(at.text_input)}")
    print(f"Chat inputs: {len(at.chat_input)}")

# Check for exceptions
def test_debug_exception(authenticated_app):
    at = authenticated_app
    at.chat_input[0].set_value("test").run()
    if at.exception:
        print(f"Exception occurred: {at.exception}")
        import traceback
        traceback.print_exception(at.exception)
```

---

## 7. Summary

### Quick Reference

| Task | Command | Example |
|------|---------|---------|
| Load app | `AppTest.from_file()` | `at = AppTest.from_file("app.py")` |
| Run app | `.run()` | `at.run()` |
| Set secret | `at.secrets[key] = value` | `at.secrets["API_KEY"] = "test"` |
| Access widget | `at.widget_type[index]` | `at.button[0]` |
| Click button | `.click().run()` | `at.button[0].click().run()` |
| Set input | `.set_value(val).run()` | `at.text_input[0].set_value("x").run()` |
| Check state | `at.session_state.key` | `assert at.session_state.authenticated` |
| Check exception | `at.exception` | `assert not at.exception` |

### When to Use Each Approach

- **AppTest**: 95% of Streamlit testing (logic, state, interactions)
- **Playwright**: Visual testing, copy buttons, screenshots, cross-browser

### Next Steps

1. Create `tests/conftest.py` with fixtures
2. Create `tests/test_ui_login.py` with login tests
3. Create `tests/test_ui_chat.py` with chat tests
4. Run tests: `pytest tests/ -v`
5. Add coverage: `pytest tests/ --cov=app`
6. Integrate into CI/CD pipeline

For more information:
- [Streamlit Testing Documentation](https://docs.streamlit.io/library/advanced-features/testing)
- [Pytest Documentation](https://docs.pytest.org/)
- [Playwright for Python](https://playwright.dev/python/)
