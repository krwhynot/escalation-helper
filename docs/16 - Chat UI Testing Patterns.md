# Chat UI Testing Patterns

This guide documents specific patterns for testing chat interfaces in Streamlit, with examples from the Escalation Helper app - a chat-based SQL troubleshooting assistant.

## Overview

Chat interfaces present unique testing challenges:
- Stateful message history across interactions
- Asynchronous responses and loading states
- Complex input validation and error handling
- Dynamic UI elements (pills, follow-up questions)
- Multi-turn conversation context

This guide covers patterns for testing these scenarios using Streamlit's AppTest framework.

## 1. Message Flow Testing

### Testing Message Submission

The most basic chat test: verify user messages are captured and stored correctly.

```python
def test_user_message_appears():
    """Verify user message is added to session state"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.run()

    # Submit a message
    at.chat_input[0].set_value("How do I void an order?").run()

    # User message should be in session
    user_msgs = [m for m in at.session_state.messages if m["role"] == "user"]
    assert len(user_msgs) >= 1
    assert "void" in user_msgs[-1]["content"].lower()
```

**Key Pattern:** Always filter `session_state.messages` by role to isolate user vs assistant messages.

### Testing Assistant Response Appears

Verify the app generates a response after user input.

```python
def test_assistant_response_appears():
    """Verify assistant responds to user input"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.run()

    # Submit query
    at.chat_input[0].set_value("test query").run()

    # Assistant should respond
    assistant_msgs = [m for m in at.session_state.messages if m["role"] == "assistant"]
    assert len(assistant_msgs) >= 1
    assert len(assistant_msgs[-1]["content"]) > 0
```

**Practical Tip:** Don't assert on exact response content in unit tests. Content varies based on embeddings/LLM. Instead, verify:
- Response exists
- Response is non-empty
- Response contains expected structure (SQL blocks, markdown)

### Testing Conversation History

Multi-turn conversations must maintain history.

```python
def test_multiple_messages_persist():
    """Verify conversation history persists across multiple inputs"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.session_state.messages = []
    at.run()

    # Send multiple messages
    at.chat_input[0].set_value("message 1").run()
    first_count = len(at.session_state.messages)

    at.chat_input[0].set_value("message 2").run()
    second_count = len(at.session_state.messages)

    # History should grow
    assert second_count > first_count
    assert len(at.session_state.messages) >= 4  # 2 user + 2 assistant
```

### Testing Conversation Context

Follow-up questions depend on previous context.

```python
def test_conversation_context_maintained():
    """Test that follow-up questions have access to prior context"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.session_state.messages = [
        {"role": "user", "content": "printer issues"},
        {"role": "assistant", "content": "What kind of printer issue?"}
    ]
    at.run()

    # Context should be available for rendering
    assert len(at.session_state.messages) == 2

    # Submit follow-up
    at.chat_input[0].set_value("receipt won't print").run()

    # New messages should be appended
    assert len(at.session_state.messages) >= 3
```

**Pattern:** Pre-populate `session_state.messages` to test mid-conversation scenarios without rebuilding entire conversation flow.

## 2. Response Rendering Testing

### SQL Code Block Detection

For SQL troubleshooting apps, verify responses contain properly formatted SQL.

```python
def test_sql_in_response():
    """Verify responses contain SQL code blocks when expected"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.session_state.messages = [
        {"role": "user", "content": "find employee by name"},
        {"role": "assistant", "content": "Here's how to find an employee:\n\n```sql\nSELECT * FROM Employee WHERE Name LIKE '%John%'\n```\n\nThis query searches by partial name match."}
    ]
    at.run()

    # Check assistant message contains SQL
    assistant_msg = at.session_state.messages[-1]
    assert "SELECT" in assistant_msg["content"]
    # Streamlit chat accepts both ```sql and ``` for syntax highlighting
    assert "```" in assistant_msg["content"]
```

**Practical Tip:** Test with realistic mock data. Copy actual assistant responses from your app's logs to ensure your tests match real-world output.

### Markdown Formatting Preservation

Chat messages often use markdown for structure.

```python
def test_markdown_formatting():
    """Verify markdown is preserved in messages"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.session_state.messages = [
        {"role": "assistant", "content": "**Step 1:** Check permissions\n\n- Item 1\n- Item 2\n\n**Step 2:** Run query"}
    ]
    at.run()

    msg = at.session_state.messages[0]["content"]
    # Verify markdown syntax is preserved
    assert "**Step 1:**" in msg
    assert "- Item 1" in msg
    assert "\n" in msg  # Line breaks preserved
```

### Testing Response Structure

For consistent UX, responses should follow a structure.

```python
def test_response_has_explanation():
    """Verify responses include explanations, not just SQL"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.session_state.messages = [
        {"role": "user", "content": "void order"},
        {"role": "assistant", "content": "To void an order:\n\n```sql\nUPDATE Orders SET Status = 'Voided'\n```\n\nNote: Ensure user has void permissions."}
    ]
    at.run()

    assistant_msg = at.session_state.messages[-1]["content"]

    # Should have SQL
    assert "```" in assistant_msg
    # Should have explanation
    assert len(assistant_msg.replace("```sql", "").replace("```", "").strip()) > 50
```

## 3. State Management Testing

### Loading States

Chat apps typically show loading indicators during search/LLM calls.

```python
def test_search_state_tracking():
    """Verify searching state can be managed"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.run()

    # Simulate starting a search
    at.session_state.searching = True
    at.run()
    assert at.session_state.searching == True

    # Simulate completing search
    at.session_state.searching = False
    at.run()
    assert at.session_state.searching == False
```

**Limitation:** AppTest cannot verify visual loading spinners (`st.spinner`, `st.status`). These require browser-based testing with Playwright.

### Error States

Robust error handling is critical for chat UX.

```python
def test_no_results_handling():
    """Verify graceful handling when no results found"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.run()

    # Query that might return no results
    at.chat_input[0].set_value("xyznonexistentquery123").run()

    # Should handle gracefully without exception
    assert not at.exception

    # Should provide helpful message
    assistant_msgs = [m for m in at.session_state.messages if m["role"] == "assistant"]
    if len(assistant_msgs) > 0:
        last_response = assistant_msgs[-1]["content"].lower()
        # Should indicate no results found
        assert any(phrase in last_response for phrase in ["no results", "couldn't find", "try rephrasing"])
```

### API Error Handling

Test behavior when external services fail.

```python
def test_api_error_graceful():
    """Test behavior when OpenAI API fails"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.secrets["OPENAI_API_KEY"] = "invalid-key-12345"
    at.run()

    # Should show auth error, not crash
    at.chat_input[0].set_value("test query").run()

    # Either exception is caught or error is displayed
    if at.exception:
        # Acceptable: exception bubbles up in test
        assert "api" in str(at.exception).lower() or "auth" in str(at.exception).lower()
    else:
        # Preferred: error shown to user
        assert len(at.error) > 0 or len(at.warning) > 0
```

**Practical Tip:** Use `try/except` in your app code to catch API errors and convert them to user-friendly messages rather than crashing.

### Empty States

Test initial and cleared states.

```python
def test_empty_chat_initial():
    """Verify empty state on first load"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.session_state.messages = []
    at.run()

    # Should show welcome or empty state
    assert len(at.session_state.messages) == 0

    # Chat input should still be available
    assert len(at.chat_input) > 0

def test_cleared_chat():
    """Verify conversation can be cleared"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.session_state.messages = [
        {"role": "user", "content": "test"},
        {"role": "assistant", "content": "response"}
    ]
    at.run()

    # Simulate clear button click
    at.session_state.messages = []
    at.run()

    assert len(at.session_state.messages) == 0
```

## 4. Input Handling Tests

### Special Characters and Injection

Chat inputs must handle special characters safely.

```python
def test_special_characters_input():
    """Verify SQL-like input doesn't break the app"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.run()

    # Test potentially problematic SQL characters
    at.chat_input[0].set_value("SELECT * FROM users; DROP TABLE--").run()
    assert not at.exception

    # Message should be stored as-is
    user_msgs = [m for m in at.session_state.messages if m["role"] == "user"]
    assert "DROP TABLE" in user_msgs[-1]["content"]

def test_quote_handling():
    """Verify quotes don't break string handling"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.run()

    at.chat_input[0].set_value("Find orders with 'quote' and \"double quote\"").run()
    assert not at.exception
```

**Security Note:** While testing that special characters don't crash the app, ensure your actual search/query logic parameterizes inputs to prevent SQL injection.

### Unicode and Internationalization

```python
def test_unicode_input():
    """Verify unicode characters are handled correctly"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.run()

    # Test accented characters
    at.chat_input[0].set_value("café résumé naïve").run()
    assert not at.exception

    # Test emoji (common in chat)
    at.chat_input[0].set_value("printer issue 🖨️").run()
    assert not at.exception

    # Verify stored correctly
    user_msgs = [m for m in at.session_state.messages if m["role"] == "user"]
    assert "café" in user_msgs[0]["content"]
```

### Long Input Handling

```python
def test_long_query():
    """Verify app handles very long queries gracefully"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.run()

    # Create very long query (500 words)
    long_query = "test " * 500
    at.chat_input[0].set_value(long_query).run()

    # Should handle without crash
    assert not at.exception

    # Optionally verify truncation if implemented
    user_msgs = [m for m in at.session_state.messages if m["role"] == "user"]
    stored_content = user_msgs[-1]["content"]
    assert len(stored_content) > 0  # Not silently dropped

def test_empty_input():
    """Verify empty input is handled"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.run()

    # Try to submit empty message
    at.chat_input[0].set_value("").run()

    # Should either block submission or handle gracefully
    # (Streamlit chat_input typically blocks empty submissions)
    assert not at.exception
```

## 5. Follow-up Questions Testing

The Escalation Helper uses a follow-up question system when initial results are uncertain.

### Testing Follow-up Triggers

```python
def test_followup_question_triggered():
    """Test that low-confidence results trigger follow-up"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.session_state.followup_active = True
    at.session_state.pending_followup = "printer"
    at.run()

    # Follow-up state should be active
    assert at.session_state.followup_active == True
    assert at.session_state.pending_followup == "printer"

def test_followup_question_content():
    """Verify follow-up questions are asked correctly"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.session_state.followup_active = True
    at.session_state.pending_followup = "payment"
    at.run()

    # Should have a message prompting for more info
    # (Implementation-dependent - adjust to match your app)
    if len(at.session_state.messages) > 0:
        last_msg = at.session_state.messages[-1]
        if last_msg["role"] == "assistant":
            assert "payment" in last_msg["content"].lower() or "?" in last_msg["content"]
```

### Testing Category Detection

```python
def test_followup_category_detection():
    """Test category detection from user queries"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.run()

    # Submit query that should trigger printer category
    at.chat_input[0].set_value("receipt printer not working").run()

    # Verify category detected (check session state or response)
    # This is implementation-dependent
    if hasattr(at.session_state, 'detected_category'):
        assert at.session_state.detected_category == "printer"
```

### Testing Follow-up Response Flow

```python
def test_followup_answered():
    """Test that answering follow-up improves results"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True

    # Set up follow-up state
    at.session_state.messages = [
        {"role": "user", "content": "printer issue"},
        {"role": "assistant", "content": "What type of printer issue? Receipt, kitchen, or label?"}
    ]
    at.session_state.followup_active = True
    at.session_state.original_query = "printer issue"
    at.run()

    # Answer follow-up
    at.chat_input[0].set_value("receipt printer").run()

    # Should combine with original query
    # (Implementation-dependent - check your search logic)
    user_msgs = [m for m in at.session_state.messages if m["role"] == "user"]
    assert len(user_msgs) >= 2
```

## 6. Quick Search Pills Testing

Many chat interfaces include quick-action buttons or pills.

```python
def test_pills_exist():
    """Verify quick search pills are rendered"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.run()

    # Check if pills component exists
    # Note: st.pills support in AppTest varies by Streamlit version
    if hasattr(at, 'pills') and len(at.pills) > 0:
        assert len(at.pills[0].options) > 0

def test_pill_selection():
    """Test clicking a quick search pill"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.run()

    # If pills are implemented as buttons
    if len(at.button) > 1:  # First might be clear button
        # Click second button (example pill)
        at.button[1].click().run()

        # Should trigger a search
        assert len(at.session_state.messages) > 0
```

**Practical Tip:** Pills are often implemented as `st.button` or `st.pills`. Verify behavior by checking session state changes after interaction.

## 7. Accessibility Considerations

Full accessibility testing requires browser automation (Playwright + axe-core), but AppTest can verify basic patterns.

### Label Verification

```python
def test_input_has_label():
    """Verify inputs have accessible labels"""
    at = AppTest.from_file("app.py")
    at.run()

    # Check password input has label
    if len(at.text_input) > 0:
        assert at.text_input[0].label is not None
        assert len(at.text_input[0].label) > 0

def test_chat_input_has_placeholder():
    """Verify chat input has helpful placeholder"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.run()

    # Chat input should have placeholder text
    if len(at.chat_input) > 0:
        # Placeholder helps users understand what to type
        assert at.chat_input[0].placeholder is not None or at.chat_input[0].label is not None
```

### Error Message Clarity

```python
def test_error_messages_descriptive():
    """Verify error messages are user-friendly"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.secrets["OPENAI_API_KEY"] = ""
    at.run()

    at.chat_input[0].set_value("test").run()

    # If error occurs, message should be clear
    if len(at.error) > 0:
        error_text = str(at.error[0]).lower()
        # Should mention API key, not just "error"
        assert "api" in error_text or "key" in error_text or "configuration" in error_text

def test_no_results_message_helpful():
    """Verify no-results messages guide users"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.run()

    at.chat_input[0].set_value("qwertyuiopasdfghjkl").run()

    assistant_msgs = [m for m in at.session_state.messages if m["role"] == "assistant"]
    if len(assistant_msgs) > 0:
        response = assistant_msgs[-1]["content"].lower()
        # Should suggest next steps
        helpful_phrases = ["try", "instead", "different", "help", "rephrasing"]
        assert any(phrase in response for phrase in helpful_phrases)
```

## 8. Performance and Efficiency Testing

### Response Time Tracking

```python
import time

def test_response_time_reasonable():
    """Verify responses return in reasonable time"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.run()

    start = time.time()
    at.chat_input[0].set_value("test query").run()
    duration = time.time() - start

    # Should respond in under 30 seconds (adjust based on your LLM)
    assert duration < 30
```

**Note:** This tests total execution time in AppTest, not actual user-perceived latency. Use Playwright for real browser timing.

### Message Limit Testing

```python
def test_message_history_limit():
    """Verify old messages are pruned to prevent memory issues"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.session_state.messages = []
    at.run()

    # Add many messages
    for i in range(100):
        at.session_state.messages.append({"role": "user", "content": f"message {i}"})
        at.session_state.messages.append({"role": "assistant", "content": f"response {i}"})

    at.run()

    # If pruning is implemented, history should be limited
    # (Adjust assertion based on your MAX_HISTORY setting)
    if hasattr(at.session_state, 'MAX_HISTORY'):
        assert len(at.session_state.messages) <= at.session_state.MAX_HISTORY
```

## 9. Integration Testing Patterns

### End-to-End Conversation Flow

```python
def test_complete_conversation_flow():
    """Test a realistic multi-turn conversation"""
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.session_state.messages = []
    at.run()

    # Turn 1: Initial question
    at.chat_input[0].set_value("How do I void an order?").run()
    assert len([m for m in at.session_state.messages if m["role"] == "assistant"]) >= 1

    # Turn 2: Follow-up question
    at.chat_input[0].set_value("What if the order is already closed?").run()
    assert len(at.session_state.messages) >= 4  # 2 user + 2 assistant

    # Turn 3: Clarification
    at.chat_input[0].set_value("Can you show me the SQL?").run()
    assert len(at.session_state.messages) >= 6

    # Final response should contain SQL
    assistant_msgs = [m for m in at.session_state.messages if m["role"] == "assistant"]
    last_response = assistant_msgs[-1]["content"]
    assert "SELECT" in last_response or "UPDATE" in last_response
```

### Search Quality Validation

```python
def test_search_returns_relevant_results():
    """Verify search returns relevant SQL for common queries"""
    test_cases = [
        ("void order", ["UPDATE", "Order", "Status"]),
        ("find employee", ["SELECT", "Employee", "WHERE"]),
        ("printer setup", ["printer", "receipt", "kitchen"])
    ]

    for query, expected_terms in test_cases:
        at = AppTest.from_file("app.py")
        at.session_state.authenticated = True
        at.session_state.messages = []
        at.run()

        at.chat_input[0].set_value(query).run()

        assistant_msgs = [m for m in at.session_state.messages if m["role"] == "assistant"]
        assert len(assistant_msgs) > 0

        response = assistant_msgs[-1]["content"]
        # At least some expected terms should appear
        assert any(term in response for term in expected_terms)
```

## 10. Best Practices Summary

### DO:
- Test state management thoroughly (messages, follow-ups, errors)
- Verify both success and failure paths
- Use realistic mock data from actual app usage
- Test edge cases (empty input, very long input, special characters)
- Filter messages by role when asserting on conversation state
- Pre-populate `session_state` to test mid-conversation scenarios

### DON'T:
- Assert on exact LLM response content (it varies)
- Test visual rendering details (use Playwright for that)
- Assume chat_input indices won't change as UI evolves
- Forget to authenticate before testing protected features
- Test external API reliability (mock them instead)

### For the Escalation Helper App Specifically:
- Always set `authenticated = True` before chat tests
- Test both high-confidence and low-confidence result paths
- Verify SQL code blocks are properly formatted
- Test category detection for follow-up questions
- Validate distance thresholds and reranking behavior
- Test with queries from `data/sql_reference.md` for realism

### Debugging Failed Tests:
```python
# Print full state for debugging
def test_debug_helper():
    at = AppTest.from_file("app.py")
    at.session_state.authenticated = True
    at.run()

    at.chat_input[0].set_value("test").run()

    # Debug output
    print(f"Messages: {at.session_state.messages}")
    print(f"Errors: {at.error}")
    print(f"Exceptions: {at.exception}")
    print(f"Session keys: {list(at.session_state.keys())}")
```

## 11. Example Test Suite

Here's a complete test file structure for the Escalation Helper:

```python
# tests/test_chat_ui.py
import pytest
from streamlit.testing.v1 import AppTest

class TestChatBasics:
    def test_message_submission(self):
        # Basic message flow
        pass

    def test_conversation_history(self):
        # Multiple turns
        pass

class TestResponseQuality:
    def test_sql_in_response(self):
        # SQL formatting
        pass

    def test_explanation_included(self):
        # Not just code
        pass

class TestErrorHandling:
    def test_no_results(self):
        # Graceful degradation
        pass

    def test_api_failure(self):
        # Service unavailable
        pass

class TestFollowupQuestions:
    def test_low_confidence_triggers_followup(self):
        # Distance threshold
        pass

    def test_category_detection(self):
        # Printer, payment, etc.
        pass

class TestEdgeCases:
    def test_special_characters(self):
        # SQL injection patterns
        pass

    def test_long_input(self):
        # 500+ word queries
        pass

class TestAuthentication:
    def test_unauthenticated_no_chat(self):
        # Login required
        pass

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

## Conclusion

Testing chat interfaces requires attention to:
- **State management**: Message history, loading states, error states
- **Input validation**: Special characters, long text, empty input
- **Response quality**: SQL formatting, explanations, structure
- **Error handling**: API failures, no results, edge cases
- **User experience**: Follow-ups, accessibility, helpful messages

Use AppTest for state and logic testing, and Playwright for visual/interaction testing. Together, they provide comprehensive coverage of your chat UI.
