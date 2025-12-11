# Golden Dataset Guide

This guide explains how to create and maintain a golden test dataset for evaluating the Escalation Helper RAG system. A well-maintained golden dataset is essential for measuring and improving the quality of your SQL troubleshooting assistant.

## Table of Contents

1. [What is a Golden Dataset?](#1-what-is-a-golden-dataset)
2. [Structure of a Test Case](#2-structure-of-a-test-case)
3. [Minimum Viable Dataset Size](#3-minimum-viable-dataset-size)
4. [Collecting Test Cases](#4-collecting-test-cases)
5. [Labeling Best Practices](#5-labeling-best-practices)
6. [Complete Golden Dataset Template](#6-complete-golden-dataset-template)
7. [Using the Dataset in Tests](#7-using-the-dataset-in-tests)
8. [Maintaining the Dataset](#8-maintaining-the-dataset)

---

## 1. What is a Golden Dataset?

### Definition

A golden dataset is a curated set of test cases with known-good answers that serves as ground truth for evaluating your RAG system. Each test case contains:

- **Query**: The user's natural language question
- **Expected Retrieved Docs**: Which documents should be retrieved from the knowledge base
- **Expected Answer**: What the final response should contain

Think of it as a "master answer key" for your RAG system.

### Why You Need One

Without a golden dataset, you're flying blind. Here's what it provides:

#### 1. Reproducible Test Results
```python
# Before golden dataset:
"I think the system works better now... maybe?"

# With golden dataset:
"Pass rate improved from 78% to 92% after reranking implementation"
```

#### 2. Regression Testing
When you change the system (new embedding model, different chunk size, updated prompts), you can immediately see if quality improved or degraded:

```bash
# Run tests before change
$ pytest tests/test_rag.py
15 passed, 0 failed

# Make changes to chunking strategy
# Run tests again
$ pytest tests/test_rag.py
12 passed, 3 failed  # Uh oh, investigate the failures
```

#### 3. Objective Quality Measurement
Instead of subjective "it seems to work," you get metrics:
- Retrieval precision: Are we finding the right documents?
- Answer faithfulness: Does the answer match retrieved docs?
- Answer completeness: Did we include all key information?

#### 4. Compare Different Configurations
Test different approaches systematically:

| Configuration | Chunk Size | Embedding Model | Reranking | Pass Rate |
|--------------|------------|-----------------|-----------|-----------|
| Baseline | 2000 | ada-002 | No | 78% |
| Config A | 1000 | ada-002 | Yes | 85% |
| Config B | 2000 | text-3-small | Yes | 92% |

### Real-World Example: Escalation Helper

For the HungerRush SQL troubleshooting assistant, a golden dataset helps answer:
- "Does the system correctly identify void permission issues?"
- "When a user asks about printers, do we return printer-related SQL queries?"
- "Are we handling ambiguous queries appropriately with follow-up questions?"

---

## 2. Structure of a Test Case

### Required Fields

Every test case must include these core fields:

```json
{
    "id": "void-001",
    "query": "cashier can't void an order",
    "category": "order",
    "expected_docs": ["sql_reference.md#problem-37"],
    "expected_answer_contains": ["SecGrp", "VoidPerm", "permission"],
    "reference_answer": "Check the SecGrp table for void permissions. Run: SELECT * FROM SecGrp WHERE SecGrpID = (SELECT SecGrpID FROM Employee WHERE EmpID = ?). Look for VoidPerm column.",
    "difficulty": "easy",
    "tags": ["permissions", "void", "security"]
}
```

#### Field Descriptions

**id** (string, required)
- Unique identifier for the test case
- Use a descriptive naming scheme: `{category}-{number}`
- Examples: `void-001`, `printer-004`, `payment-002`

**query** (string, required)
- The exact user question to test
- Write it as a real user would (natural language, possibly imperfect)
- Examples:
  - Good: "cashier can't void an order"
  - Good: "receipt printer not printing"
  - Bad: "What is the SQL query for void permissions?" (too technical)

**category** (string, required)
- Which category this query belongs to
- For Escalation Helper: `printer`, `payment`, `employee`, `order`, `menu`, `cash`
- Used to validate follow-up question flow

**expected_docs** (array, required)
- List of document IDs that should be retrieved
- Format: `filename#section` or just `filename`
- Examples:
  - `["sql_reference.md#problem-37"]`
  - `["sql_reference.md#printer-config", "data/confluence/printer-troubleshooting.md"]`

**expected_answer_contains** (array, required)
- Key phrases that MUST appear in the answer
- Use exact technical terms (table names, column names, SQL keywords)
- Examples:
  - `["SecGrp", "VoidPerm", "permission"]`
  - `["Printer", "PrinterID", "Station"]`

**reference_answer** (string, required)
- The complete, ideal answer
- Written by a domain expert (HungerRush installer)
- Should include SQL queries when appropriate

**difficulty** (string, required)
- How hard is this query to answer?
- Values: `easy`, `medium`, `hard`
- Helps track performance across complexity levels

**tags** (array, required)
- Searchable labels for grouping tests
- Examples: `["permissions", "SQL", "troubleshooting"]`

### Optional Fields

Add these for more sophisticated testing:

```json
{
    "context_keywords": ["SecGrp", "void", "permission"],
    "negative_keywords": ["printer", "payment"],
    "min_faithfulness": 0.9,
    "min_answer_relevancy": 0.85,
    "should_trigger_followup": false,
    "expected_followup_category": "order",
    "notes": "Edge case - multiple valid SQL queries exist",
    "related_test_ids": ["void-002", "employee-003"]
}
```

#### Optional Field Descriptions

**context_keywords** (array)
- Keywords that should appear in retrieved document context
- Stricter than `expected_answer_contains` (checks retrieval quality)

**negative_keywords** (array)
- Words that should NOT appear in the answer
- Useful for testing category separation
- Example: For a void query, `["printer", "payment"]` shouldn't appear

**min_faithfulness** (float, 0.0-1.0)
- Minimum RAGAS faithfulness score (answer grounded in retrieved docs)
- Default: 0.8

**min_answer_relevancy** (float, 0.0-1.0)
- Minimum RAGAS answer relevancy score
- Default: 0.8

**should_trigger_followup** (boolean)
- Whether this query should trigger follow-up questions
- Useful for testing low-confidence detection

**expected_followup_category** (string)
- If follow-up triggered, which category should it detect?

**notes** (string)
- Free-text explanation of edge cases or special considerations

**related_test_ids** (array)
- Links to similar test cases
- Helps identify clusters of related issues

---

## 3. Minimum Viable Dataset Size

### General Recommendations

| Project Stage | Minimum Tests | Recommended | Notes |
|--------------|---------------|-------------|-------|
| Prototype | 10-15 | 20 | Cover happy paths only |
| Production | 30-50 | 100+ | Include edge cases |
| Enterprise | 100+ | 500+ | Comprehensive coverage |

### For Escalation Helper Specifically

**Minimum Viable: 20 test cases**
- At least 3 test cases per category (6 categories × 3 = 18)
- 2+ edge cases (ambiguous queries, multi-category issues)

**Target: 50 test cases**
- 8-10 test cases per category
- Mix of easy (40%), medium (40%), hard (20%) difficulty
- Coverage of common troubleshooting patterns

**Long-term: 100+ test cases**
- Add cases from real user queries
- Include seasonal issues (year-end, busy hours)
- Cover all major SQL tables and joins

### Coverage Matrix

Ensure balanced coverage across dimensions:

| Category | Easy | Medium | Hard | Total |
|----------|------|--------|------|-------|
| printer | 3 | 3 | 2 | 8 |
| payment | 3 | 3 | 2 | 8 |
| employee | 3 | 3 | 2 | 8 |
| order | 3 | 3 | 2 | 8 |
| menu | 3 | 3 | 2 | 8 |
| cash | 3 | 3 | 2 | 8 |
| **Total** | **18** | **18** | **12** | **48** |

### Quality Over Quantity

It's better to have 20 high-quality, expert-validated test cases than 100 rushed, poorly-labeled cases.

**High-quality test case:**
```json
{
    "id": "void-001",
    "query": "cashier can't void an order",
    "category": "order",
    "expected_docs": ["sql_reference.md#problem-37"],
    "expected_answer_contains": ["SecGrp", "VoidPerm", "SELECT"],
    "reference_answer": "Check the SecGrp table for void permissions...",
    "difficulty": "easy",
    "tags": ["permissions", "void"],
    "notes": "Common issue. Verified by installer team 2024-12-01."
}
```

**Low-quality test case:**
```json
{
    "id": "test1",
    "query": "something wrong",
    "expected_docs": ["some doc"],
    "expected_answer_contains": ["fix it"]
}
```

---

## 4. Collecting Test Cases

### Source 1: Real User Queries

This is the BEST source for test cases because it reflects actual usage.

**Implementation:**

1. Add logging to `app.py`:

```python
import json
from datetime import datetime

def log_query(query, response, distance, category):
    """Log user queries for dataset creation"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "response": response[:200],  # First 200 chars
        "min_distance": distance,
        "category": category
    }

    with open('logs/user_queries.jsonl', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
```

2. Review logs monthly and extract successful queries:

```python
import json

# Read logs
with open('logs/user_queries.jsonl') as f:
    logs = [json.loads(line) for line in f]

# Filter successful queries (low distance = good retrieval)
successful = [log for log in logs if log['min_distance'] < 0.30]

# Group by category
from collections import defaultdict
by_category = defaultdict(list)
for log in successful:
    by_category[log['category']].append(log['query'])

# Show top queries per category
for category, queries in by_category.items():
    print(f"\n{category}:")
    for query in queries[:5]:
        print(f"  - {query}")
```

**Example Output:**
```
printer:
  - receipt printer not printing
  - kitchen printer printing duplicate tickets
  - barcode not printing on receipt

payment:
  - credit card declined but customer was charged
  - gift card balance incorrect
```

### Source 2: Domain Expert Input

Work directly with HungerRush installers who troubleshoot daily.

**Interview Questions:**

1. "What are the top 10 issues you help restaurants with?"
2. "What questions do users ask most frequently?"
3. "What's the most confusing issue you've encountered?"
4. "Are there any 'gotchas' that trip people up?"

**Example Interview Session:**

```
Interviewer: What's a common void-related issue?

Installer: Oh, definitely permission problems. A manager sets up a new
cashier and forgets to enable void permissions in their security group.
The cashier tries to void an order and gets an error.

Interviewer: How would a user describe this problem?

Installer: Usually something like "cashier can't void" or "void button
not working" or "need to void an order but can't."

Interviewer: What's the fix?

Installer: Check the SecGrp table for the employee's security group and
make sure VoidPerm is set to 1. The query is:
SELECT * FROM SecGrp WHERE SecGrpID = (SELECT SecGrpID FROM Employee
WHERE EmpID = ?).
```

**Convert to Test Case:**
```json
{
    "id": "void-001",
    "query": "cashier can't void an order",
    "category": "order",
    "expected_docs": ["sql_reference.md#problem-37"],
    "expected_answer_contains": ["SecGrp", "VoidPerm", "permission"],
    "reference_answer": "Check the SecGrp table for void permissions. Run: SELECT * FROM SecGrp WHERE SecGrpID = (SELECT SecGrpID FROM Employee WHERE EmpID = ?). Look for VoidPerm column.",
    "difficulty": "easy",
    "tags": ["permissions", "void", "security"],
    "notes": "Most common permission issue according to installer team"
}
```

### Source 3: Existing Documentation

Mine your existing knowledge base for test cases.

**Method:**

1. Open `/home/krwhynot/projects/escalation-helper/data/sql_reference.md`
2. For each problem section, create 2-3 query variants

**Example:**

From documentation:
```markdown
## Problem 37: Employee doesn't have permissions to void orders

**Query:**
SELECT * FROM SecGrp WHERE SecGrpID = (SELECT SecGrpID FROM Employee WHERE EmpID = ?)
```

Create test cases with different phrasings:

```json
[
    {
        "id": "void-001",
        "query": "cashier can't void an order",
        "difficulty": "easy"
    },
    {
        "id": "void-002",
        "query": "void button doesn't work",
        "difficulty": "easy"
    },
    {
        "id": "void-003",
        "query": "permission denied when trying to void",
        "difficulty": "medium"
    },
    {
        "id": "void-004",
        "query": "how do I check void permissions for an employee",
        "difficulty": "medium",
        "notes": "More technical phrasing - tests if system handles direct questions"
    }
]
```

### Source 4: Synthetic Generation with RAGAS

Use RAGAS to automatically generate test cases from your documents.

**Installation:**
```bash
pip install ragas langchain-community
```

**Generation Script:**

```python
from ragas.testset.generators import TestsetGenerator
from ragas.testset.evolutions import simple, reasoning, multi_context
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Load your documents
loader = DirectoryLoader(
    '/home/krwhynot/projects/escalation-helper/data/',
    glob="**/*.md",
    loader_cls=TextLoader
)
documents = loader.load()

# Initialize generator
generator = TestsetGenerator.with_openai()

# Generate test cases
testset = generator.generate_with_langchain_docs(
    documents=documents,
    test_size=20,
    distributions={
        simple: 0.5,        # 10 simple single-doc queries
        reasoning: 0.25,    # 5 queries requiring reasoning
        multi_context: 0.25 # 5 queries needing multiple docs
    }
)

# Convert to golden dataset format
golden_cases = []
for i, test in enumerate(testset.test_data):
    golden_cases.append({
        "id": f"synthetic-{i:03d}",
        "query": test['question'],
        "expected_answer_contains": [],  # Fill in manually
        "reference_answer": test['answer'],
        "difficulty": "medium",
        "tags": ["synthetic"],
        "notes": f"Generated using RAGAS {test['evolution_type']}"
    })

print(json.dumps(golden_cases, indent=2))
```

**Pros:**
- Fast generation of test cases
- Good coverage of different query types
- Can generate edge cases you might not think of

**Cons:**
- Requires manual review and cleanup
- May generate unrealistic queries
- Still needs domain expert validation

**Best Practice:** Use synthetic generation to create a starting point, then have installers review and refine each test case.

---

## 5. Labeling Best Practices

### Use Multiple Reviewers

Never rely on a single person to label test cases.

**Workflow:**

1. **Initial Labeling** (Reviewer 1)
   - Creates test case structure
   - Writes reference answer
   - Tags difficulty and category

2. **Review** (Reviewer 2)
   - Validates expected docs are correct
   - Checks reference answer accuracy
   - Suggests improvements

3. **Resolution** (Both)
   - Discuss any disagreements
   - Update test case
   - Mark as "validated"

**Example Disagreement:**

```json
// Reviewer 1's version
{
    "id": "printer-001",
    "query": "receipt printer not printing",
    "difficulty": "easy"
}

// Reviewer 2's feedback
{
    "comment": "This should be 'medium' - printer issues can involve
                Station table, Printer table, AND hardware checks",
    "suggested_difficulty": "medium"
}

// Final version (after discussion)
{
    "id": "printer-001",
    "query": "receipt printer not printing",
    "difficulty": "medium",
    "notes": "Requires checking multiple tables (Printer, Station) and
              considering hardware issues"
}
```

### Graded Relevance

Instead of binary relevant/not-relevant, use a scale:

| Score | Label | Description | Example |
|-------|-------|-------------|---------|
| 3 | Highly relevant | Directly answers the query with exact SQL | Document shows `SELECT * FROM SecGrp WHERE...` for void permission query |
| 2 | Somewhat relevant | Provides useful context but not complete answer | Document explains SecGrp table structure but no query |
| 1 | Marginally relevant | Tangentially related | Document mentions permissions but for different feature |
| 0 | Not relevant | Unrelated | Document about printer configuration for void query |

**Use in Test Cases:**

```json
{
    "id": "void-001",
    "query": "cashier can't void an order",
    "expected_docs": [
        {
            "doc_id": "sql_reference.md#problem-37",
            "relevance": 3,
            "reason": "Contains exact SQL query for void permissions"
        },
        {
            "doc_id": "sql_reference.md#employee-permissions",
            "relevance": 2,
            "reason": "Explains SecGrp table structure"
        }
    ]
}
```

**Benefits:**
- More nuanced evaluation
- Helps tune retrieval threshold
- Identifies "close but not perfect" matches

### Inter-Rater Agreement

Track how often reviewers agree using Cohen's Kappa.

**Calculation:**

```python
from sklearn.metrics import cohen_kappa_score

# Reviewer 1's relevance scores for 10 test cases
reviewer1 = [3, 3, 2, 1, 3, 2, 0, 3, 2, 1]

# Reviewer 2's relevance scores for same 10 test cases
reviewer2 = [3, 2, 2, 1, 3, 2, 0, 3, 1, 2]

# Calculate agreement
kappa = cohen_kappa_score(reviewer1, reviewer2)
print(f"Cohen's Kappa: {kappa:.2f}")

# Interpretation
if kappa > 0.8:
    print("Excellent agreement")
elif kappa > 0.6:
    print("Good agreement")
elif kappa > 0.4:
    print("Moderate agreement - discuss differences")
else:
    print("Poor agreement - need clearer guidelines")
```

**Target:** Aim for Kappa > 0.7

### Version Control

Store golden dataset in git alongside code.

**File Structure:**
```
escalation-helper/
├── tests/
│   ├── golden_dataset.json          # Main dataset
│   ├── golden_dataset_CHANGELOG.md  # Version history
│   └── test_rag_evaluation.py       # Test runner
```

**Semantic Versioning:**

```
v1.0.0 - Initial dataset (20 test cases)
v1.1.0 - Added 10 payment test cases
v1.2.0 - Added difficulty labels to all cases
v2.0.0 - Breaking change: restructured expected_docs format
```

**CHANGELOG.md Template:**

```markdown
# Golden Dataset Changelog

All notable changes to the golden test dataset will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Test case payment-005 for split tender issues

### Changed
- Updated printer-002 reference answer with new SQL query

## [1.1.0] - 2024-03-15

### Added
- 5 new payment test cases (payment-003 through payment-007)
- Graded relevance scores for all test cases
- `notes` field explaining edge cases

### Changed
- Updated printer-002 reference answer to include Station table join
- Increased difficulty of void-003 from "easy" to "medium"

### Removed
- Deprecated order-003 (replaced by order-005 with better phrasing)

## [1.0.0] - 2024-12-10

### Added
- Initial dataset with 20 test cases
- Coverage across all 6 categories (printer, payment, employee, order, menu, cash)
- Basic structure: query, expected_docs, reference_answer
```

**Git Workflow:**

```bash
# Make changes to dataset
vi tests/golden_dataset.json

# Update changelog
vi tests/golden_dataset_CHANGELOG.md

# Commit with descriptive message
git add tests/golden_dataset.json tests/golden_dataset_CHANGELOG.md
git commit -m "feat(tests): add 5 payment test cases for v1.1.0"

# Tag the release
git tag -a v1.1.0 -m "Golden dataset v1.1.0: Added payment test cases"
git push origin v1.1.0
```

---

## 6. Complete Golden Dataset Template

Here's a production-ready golden dataset for Escalation Helper with 15+ diverse test cases.

### File: `/home/krwhynot/projects/escalation-helper/tests/golden_dataset.json`

```json
{
    "metadata": {
        "version": "1.0.0",
        "created": "2024-12-10",
        "last_updated": "2024-12-10",
        "description": "Golden test dataset for Escalation Helper RAG evaluation",
        "total_test_cases": 15,
        "categories": ["printer", "payment", "employee", "order", "menu", "cash"],
        "difficulty_distribution": {
            "easy": 6,
            "medium": 6,
            "hard": 3
        }
    },
    "test_cases": [
        {
            "id": "void-001",
            "query": "cashier can't void an order",
            "category": "order",
            "expected_docs": ["sql_reference.md#problem-37"],
            "expected_answer_contains": ["SecGrp", "VoidPerm", "permission", "Employee"],
            "reference_answer": "Check the SecGrp table for void permissions. Run: SELECT * FROM SecGrp WHERE SecGrpID = (SELECT SecGrpID FROM Employee WHERE EmpID = ?). Look for VoidPerm column - it should be set to 1 to allow voids.",
            "difficulty": "easy",
            "tags": ["permissions", "void", "security", "employee"],
            "should_trigger_followup": false,
            "notes": "Most common permission issue. Verified by installer team 2024-12-01."
        },
        {
            "id": "printer-001",
            "query": "receipt printer not printing",
            "category": "printer",
            "expected_docs": ["sql_reference.md#printer-config"],
            "expected_answer_contains": ["Printer", "PrinterID", "Station", "Active"],
            "reference_answer": "Check printer configuration: SELECT * FROM Printer WHERE Active = 1. Verify station assignment in Station table: SELECT StationID, PrinterID FROM Station WHERE StationID = ?. Also check physical printer connection and drivers.",
            "difficulty": "medium",
            "tags": ["printer", "hardware", "configuration", "receipt"],
            "should_trigger_followup": false
        },
        {
            "id": "payment-001",
            "query": "credit card declined but customer was charged",
            "category": "payment",
            "expected_docs": ["sql_reference.md#payment-issues"],
            "expected_answer_contains": ["Payment", "Transaction", "Tender", "Status"],
            "reference_answer": "Check Payment table for transaction status. Query: SELECT * FROM Payment WHERE OrderID = ? AND TenderType = 'CC'. Look for Status field - if 'Approved' but order shows declined, there may be a communication issue with payment processor. Check gateway logs.",
            "difficulty": "hard",
            "tags": ["payment", "credit card", "reconciliation", "transaction"],
            "should_trigger_followup": false,
            "notes": "Edge case - requires checking both POS database and payment processor logs"
        },
        {
            "id": "employee-001",
            "query": "employee can't clock in",
            "category": "employee",
            "expected_docs": ["sql_reference.md#timeclock"],
            "expected_answer_contains": ["Employee", "TimeClock", "ClockIn", "Active"],
            "reference_answer": "Verify employee status and time clock settings. Check: SELECT Active, AllowTimeClock FROM Employee WHERE EmpID = ?. Employee must be Active=1 and AllowTimeClock=1. Also verify they're not already clocked in: SELECT * FROM TimeClock WHERE EmpID = ? AND ClockOut IS NULL.",
            "difficulty": "easy",
            "tags": ["employee", "timeclock", "permissions", "punch"],
            "should_trigger_followup": false
        },
        {
            "id": "menu-001",
            "query": "menu item showing wrong price",
            "category": "menu",
            "expected_docs": ["sql_reference.md#menu-pricing"],
            "expected_answer_contains": ["MenuItem", "Price", "PriceLevel", "ItemID"],
            "reference_answer": "Check MenuItem table for pricing: SELECT * FROM MenuItem WHERE ItemID = ?. Also check PriceLevel table for time-based pricing: SELECT * FROM PriceLevel WHERE Active = 1. Verify which price level is active for the current time period.",
            "difficulty": "medium",
            "tags": ["menu", "pricing", "configuration", "item"],
            "should_trigger_followup": false
        },
        {
            "id": "cash-001",
            "query": "cash drawer won't open",
            "category": "cash",
            "expected_docs": ["sql_reference.md#cash-drawer"],
            "expected_answer_contains": ["CashDrawer", "Station", "Port"],
            "reference_answer": "Check drawer configuration in Station table. Query: SELECT CashDrawerPort, CashDrawerEnabled FROM Station WHERE StationID = ?. Verify CashDrawerEnabled = 1 and CashDrawerPort is set correctly (usually COM1 or USB). Also check physical cable connection.",
            "difficulty": "easy",
            "tags": ["cash", "hardware", "drawer", "station"],
            "should_trigger_followup": false
        },
        {
            "id": "void-002",
            "query": "manager override not working for voids",
            "category": "order",
            "expected_docs": ["sql_reference.md#problem-37", "sql_reference.md#manager-override"],
            "expected_answer_contains": ["SecGrp", "ManagerOverride", "VoidPerm", "permission"],
            "reference_answer": "Check manager security group has override permission. SELECT ManagerOverride, VoidPerm FROM SecGrp WHERE SecGrpID = (SELECT SecGrpID FROM Employee WHERE EmpID = ?). Both ManagerOverride and VoidPerm should be set to 1 for manager-level void permissions.",
            "difficulty": "medium",
            "tags": ["permissions", "void", "manager", "security", "override"],
            "should_trigger_followup": false,
            "notes": "Requires checking multiple permission fields"
        },
        {
            "id": "printer-002",
            "query": "kitchen printer printing duplicate tickets",
            "category": "printer",
            "expected_docs": ["sql_reference.md#kitchen-printer"],
            "expected_answer_contains": ["KitchenPrinter", "PrintGroup", "MenuItem", "duplicate"],
            "reference_answer": "Check print group assignments. SELECT DISTINCT pg.PrintGroupID, p.PrinterName FROM PrintGroup pg JOIN Printer p ON pg.PrinterID = p.PrinterID WHERE pg.Active = 1. Verify menu items aren't assigned to multiple print groups that route to the same printer.",
            "difficulty": "hard",
            "tags": ["printer", "kitchen", "duplicate", "printgroup"],
            "should_trigger_followup": false,
            "notes": "Complex issue - often caused by misconfigured print group routing"
        },
        {
            "id": "payment-002",
            "query": "gift card balance incorrect",
            "category": "payment",
            "expected_docs": ["sql_reference.md#gift-cards"],
            "expected_answer_contains": ["GiftCard", "Balance", "Transaction", "CardNumber"],
            "reference_answer": "Check gift card balance and transaction history: SELECT CardNumber, Balance, LastUsed FROM GiftCard WHERE CardNumber = ?. For transaction history: SELECT * FROM GiftCardTransaction WHERE CardNumber = ? ORDER BY TranDate DESC. Verify Balance matches sum of all transactions.",
            "difficulty": "medium",
            "tags": ["payment", "gift card", "balance", "transaction"],
            "should_trigger_followup": false
        },
        {
            "id": "employee-002",
            "query": "employee showing wrong hourly rate",
            "category": "employee",
            "expected_docs": ["sql_reference.md#payroll"],
            "expected_answer_contains": ["Employee", "PayRate", "Job", "EmployeeJob"],
            "reference_answer": "Check pay rate configuration: SELECT e.EmpName, j.JobTitle, ej.PayRate FROM Employee e JOIN EmployeeJob ej ON e.EmpID = ej.EmpID JOIN Job j ON ej.JobID = j.JobID WHERE e.EmpID = ?. Employee can have different rates for different job codes.",
            "difficulty": "medium",
            "tags": ["employee", "payroll", "rate", "job"],
            "should_trigger_followup": false,
            "notes": "Employees can have multiple job assignments with different rates"
        },
        {
            "id": "order-001",
            "query": "order stuck in pending status",
            "category": "order",
            "expected_docs": ["sql_reference.md#order-status"],
            "expected_answer_contains": ["Order", "Status", "OrderStatus", "Payment"],
            "reference_answer": "Check order status and payments: SELECT o.OrderID, o.Status, o.Total, SUM(p.Amount) as Paid FROM Orders o LEFT JOIN Payment p ON o.OrderID = p.OrderID WHERE o.OrderID = ? GROUP BY o.OrderID. Order may be pending if total doesn't match sum of payments.",
            "difficulty": "hard",
            "tags": ["order", "status", "payment", "pending"],
            "should_trigger_followup": false,
            "notes": "Often caused by payment/total mismatch"
        },
        {
            "id": "menu-002",
            "query": "modifier not appearing on item",
            "category": "menu",
            "expected_docs": ["sql_reference.md#modifiers"],
            "expected_answer_contains": ["Modifier", "ModifierGroup", "MenuItem", "MenuItemModGroup"],
            "reference_answer": "Check modifier group assignment: SELECT mg.GroupName, m.ModName FROM ModifierGroup mg JOIN Modifier m ON mg.ModGroupID = m.ModGroupID JOIN MenuItemModGroup mimg ON mg.ModGroupID = mimg.ModGroupID WHERE mimg.ItemID = ? AND mg.Active = 1. Verify the modifier group is active and assigned to the menu item.",
            "difficulty": "hard",
            "tags": ["menu", "modifier", "configuration", "item"],
            "should_trigger_followup": false,
            "notes": "Requires checking multiple table relationships"
        },
        {
            "id": "cash-002",
            "query": "end of day cash count doesn't match",
            "category": "cash",
            "expected_docs": ["sql_reference.md#cash-reconciliation"],
            "expected_answer_contains": ["CashCount", "Drawer", "Shift", "Expected", "Actual"],
            "reference_answer": "Compare expected vs actual: SELECT ExpectedCash, ActualCash, (ActualCash - ExpectedCash) as Variance FROM ShiftReport WHERE ShiftID = ?. Also check for voids, refunds, and paid-outs: SELECT SUM(Amount) FROM Payment WHERE ShiftID = ? AND TenderType = 'CASH'.",
            "difficulty": "medium",
            "tags": ["cash", "reconciliation", "shift", "variance"],
            "should_trigger_followup": false
        },
        {
            "id": "printer-003",
            "query": "barcode not printing on receipt",
            "category": "printer",
            "expected_docs": ["sql_reference.md#receipt-format"],
            "expected_answer_contains": ["Receipt", "Barcode", "PrintFormat", "ReceiptFormat"],
            "reference_answer": "Check receipt format settings: SELECT PrintBarcode, BarcodeType FROM ReceiptFormat WHERE FormatID = (SELECT ReceiptFormatID FROM Station WHERE StationID = ?). Verify PrintBarcode = 1 and BarcodeType is set correctly (usually 'CODE128' or 'QR').",
            "difficulty": "medium",
            "tags": ["printer", "barcode", "receipt", "format"],
            "should_trigger_followup": false
        },
        {
            "id": "employee-003",
            "query": "employee login not found",
            "category": "employee",
            "expected_docs": ["sql_reference.md#employee-login"],
            "expected_answer_contains": ["Employee", "LoginID", "Active", "EmpName"],
            "reference_answer": "Verify employee exists and is active: SELECT EmpID, EmpName, LoginID, Active FROM Employee WHERE LoginID = ? OR EmpName LIKE '%?%'. Check Active = 1 and LoginID is set. If LoginID is NULL, employee hasn't been set up for system login yet.",
            "difficulty": "easy",
            "tags": ["employee", "login", "search", "active"],
            "should_trigger_followup": false
        }
    ]
}
```

---

## 7. Using the Dataset in Tests

### Basic Test Structure

Create a pytest test file that loads and validates against the golden dataset.

### File: `/home/krwhynot/projects/escalation-helper/tests/test_rag_evaluation.py`

```python
"""
RAG evaluation tests using golden dataset.

Run with: pytest tests/test_rag_evaluation.py -v
"""

import json
import pytest
from typing import Dict, List, Any
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import search_knowledge_base, init_chroma_client

# Load golden dataset
def load_golden_dataset() -> Dict[str, Any]:
    """Load golden dataset from JSON file"""
    dataset_path = os.path.join(os.path.dirname(__file__), 'golden_dataset.json')
    with open(dataset_path) as f:
        return json.load(f)

@pytest.fixture(scope="module")
def golden_dataset():
    """Fixture to load golden dataset once for all tests"""
    return load_golden_dataset()

@pytest.fixture(scope="module")
def chroma_client():
    """Initialize ChromaDB client once for all tests"""
    return init_chroma_client()

# Parametrize tests to run once per test case
@pytest.mark.parametrize("test_case", load_golden_dataset()['test_cases'], ids=lambda tc: tc['id'])
def test_answer_contains_keywords(test_case, chroma_client):
    """Test that answer contains expected keywords"""
    query = test_case['query']
    expected_keywords = test_case['expected_answer_contains']

    # Run RAG search
    results, min_distance = search_knowledge_base(query, chroma_client)

    # Combine all results into answer text
    answer_text = " ".join([r['text'] for r in results]).lower()

    # Check each expected keyword appears
    missing_keywords = []
    for keyword in expected_keywords:
        if keyword.lower() not in answer_text:
            missing_keywords.append(keyword)

    assert not missing_keywords, f"Missing keywords: {missing_keywords}"

@pytest.mark.parametrize("test_case", load_golden_dataset()['test_cases'], ids=lambda tc: tc['id'])
def test_retrieval_distance(test_case, chroma_client):
    """Test that retrieval distance meets threshold"""
    query = test_case['query']

    # Run RAG search
    results, min_distance = search_knowledge_base(query, chroma_client)

    # Distance should be below threshold (good match)
    DISTANCE_THRESHOLD = 0.40  # From config.py
    assert min_distance < DISTANCE_THRESHOLD, \
        f"Distance {min_distance:.3f} exceeds threshold {DISTANCE_THRESHOLD}"

@pytest.mark.parametrize("test_case", load_golden_dataset()['test_cases'], ids=lambda tc: tc['id'])
def test_category_detection(test_case, chroma_client):
    """Test that correct category is detected (for follow-up questions)"""
    query = test_case['query']
    expected_category = test_case['category']

    # Run RAG search
    results, min_distance = search_knowledge_base(query, chroma_client)

    # Check if results contain category-related keywords
    answer_text = " ".join([r['text'] for r in results]).lower()

    # Category-specific keywords (simplified for example)
    category_keywords = {
        'printer': ['printer', 'print', 'receipt', 'kitchen'],
        'payment': ['payment', 'credit', 'card', 'tender', 'gift'],
        'employee': ['employee', 'emp', 'login', 'clock', 'payrate'],
        'order': ['order', 'void', 'status', 'pending'],
        'menu': ['menu', 'item', 'modifier', 'price'],
        'cash': ['cash', 'drawer', 'shift', 'count']
    }

    # Check if expected category keywords appear
    expected_keywords = category_keywords.get(expected_category, [])
    found_match = any(kw in answer_text for kw in expected_keywords)

    assert found_match, \
        f"Category '{expected_category}' keywords not found in answer"

def test_dataset_statistics(golden_dataset):
    """Test dataset has good coverage"""
    test_cases = golden_dataset['test_cases']
    metadata = golden_dataset['metadata']

    # Check minimum size
    assert len(test_cases) >= 15, "Dataset should have at least 15 test cases"

    # Check category distribution
    categories = [tc['category'] for tc in test_cases]
    unique_categories = set(categories)
    assert len(unique_categories) >= 6, "Should cover all 6 categories"

    # Check difficulty distribution
    difficulties = [tc['difficulty'] for tc in test_cases]
    assert 'easy' in difficulties, "Should have easy test cases"
    assert 'medium' in difficulties, "Should have medium test cases"
    assert 'hard' in difficulties, "Should have hard test cases"

def test_dataset_structure(golden_dataset):
    """Test all test cases have required fields"""
    required_fields = [
        'id', 'query', 'category', 'expected_docs',
        'expected_answer_contains', 'reference_answer',
        'difficulty', 'tags'
    ]

    for tc in golden_dataset['test_cases']:
        for field in required_fields:
            assert field in tc, f"Test case {tc.get('id')} missing field: {field}"

        # Validate field types
        assert isinstance(tc['expected_docs'], list)
        assert isinstance(tc['expected_answer_contains'], list)
        assert isinstance(tc['tags'], list)
        assert tc['difficulty'] in ['easy', 'medium', 'hard']

def test_no_duplicate_ids(golden_dataset):
    """Test all test case IDs are unique"""
    ids = [tc['id'] for tc in golden_dataset['test_cases']]
    assert len(ids) == len(set(ids)), "Duplicate test case IDs found"

# Summary report
def test_generate_summary_report(golden_dataset, chroma_client, tmp_path):
    """Generate a summary report of test results"""
    test_cases = golden_dataset['test_cases']

    results = {
        'total': len(test_cases),
        'passed': 0,
        'failed': 0,
        'by_category': {},
        'by_difficulty': {}
    }

    for tc in test_cases:
        query = tc['query']
        category = tc['category']
        difficulty = tc['difficulty']

        # Run search
        search_results, min_distance = search_knowledge_base(query, chroma_client)
        answer_text = " ".join([r['text'] for r in search_results]).lower()

        # Check if keywords found
        keywords_found = all(
            kw.lower() in answer_text
            for kw in tc['expected_answer_contains']
        )

        # Update results
        if keywords_found and min_distance < 0.40:
            results['passed'] += 1
            status = 'PASS'
        else:
            results['failed'] += 1
            status = 'FAIL'

        # Track by category
        if category not in results['by_category']:
            results['by_category'][category] = {'passed': 0, 'failed': 0}
        results['by_category'][category][status.lower()] += 1

        # Track by difficulty
        if difficulty not in results['by_difficulty']:
            results['by_difficulty'][difficulty] = {'passed': 0, 'failed': 0}
        results['by_difficulty'][difficulty][status.lower()] += 1

    # Write report
    report_path = tmp_path / "rag_evaluation_report.txt"
    with open(report_path, 'w') as f:
        f.write("RAG EVALUATION SUMMARY\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Total test cases: {results['total']}\n")
        f.write(f"Passed: {results['passed']} ({results['passed']/results['total']*100:.1f}%)\n")
        f.write(f"Failed: {results['failed']} ({results['failed']/results['total']*100:.1f}%)\n\n")

        f.write("By Category:\n")
        for category, stats in results['by_category'].items():
            total = stats['passed'] + stats['failed']
            pass_rate = stats['passed'] / total * 100
            f.write(f"  {category}: {stats['passed']}/{total} ({pass_rate:.1f}%)\n")

        f.write("\nBy Difficulty:\n")
        for difficulty, stats in results['by_difficulty'].items():
            total = stats['passed'] + stats['failed']
            pass_rate = stats['passed'] / total * 100
            f.write(f"  {difficulty}: {stats['passed']}/{total} ({pass_rate:.1f}%)\n")

    print(f"\nReport generated: {report_path}")

    # Report should exist
    assert report_path.exists()
```

### Running the Tests

```bash
# Run all tests
pytest tests/test_rag_evaluation.py -v

# Run specific test
pytest tests/test_rag_evaluation.py::test_answer_contains_keywords -v

# Run only easy difficulty tests
pytest tests/test_rag_evaluation.py -v -k "void-001 or printer-001 or employee-001"

# Generate HTML report
pytest tests/test_rag_evaluation.py --html=report.html --self-contained-html
```

### Example Output

```
tests/test_rag_evaluation.py::test_answer_contains_keywords[void-001] PASSED     [  6%]
tests/test_rag_evaluation.py::test_answer_contains_keywords[printer-001] PASSED  [ 13%]
tests/test_rag_evaluation.py::test_answer_contains_keywords[payment-001] FAILED  [ 20%]
tests/test_rag_evaluation.py::test_answer_contains_keywords[employee-001] PASSED [ 26%]
...

================================ FAILURES =================================
_____________ test_answer_contains_keywords[payment-001] __________________

test_case = {'id': 'payment-001', 'query': 'credit card declined but customer was charged', ...}

    def test_answer_contains_keywords(test_case, chroma_client):
        query = test_case['query']
        expected_keywords = test_case['expected_answer_contains']

        results, min_distance = search_knowledge_base(query, chroma_client)
        answer_text = " ".join([r['text'] for r in results]).lower()

        missing_keywords = []
        for keyword in expected_keywords:
            if keyword.lower() not in answer_text:
                missing_keywords.append(keyword)

>       assert not missing_keywords, f"Missing keywords: {missing_keywords}"
E       AssertionError: Missing keywords: ['Status']

========================= short test summary info =========================
FAILED tests/test_rag_evaluation.py::test_answer_contains_keywords[payment-001]
========================= 14 passed, 1 failed in 5.23s =========================
```

This tells you exactly which test failed and why - the retrieved documents didn't contain "Status" keyword.

### Advanced: RAGAS Metrics

For more sophisticated evaluation using RAGAS framework:

```python
"""
Advanced RAG evaluation using RAGAS metrics
"""

import pytest
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision
)

def test_ragas_evaluation(golden_dataset, chroma_client):
    """Run RAGAS evaluation on golden dataset"""

    # Prepare data for RAGAS
    questions = []
    ground_truths = []
    contexts = []
    answers = []

    for tc in golden_dataset['test_cases'][:5]:  # Test first 5
        query = tc['query']

        # Run RAG
        results, _ = search_knowledge_base(query, chroma_client)

        questions.append(query)
        ground_truths.append([tc['reference_answer']])
        contexts.append([r['text'] for r in results])
        answers.append(" ".join([r['text'] for r in results]))

    # Create dataset
    dataset = Dataset.from_dict({
        'question': questions,
        'answer': answers,
        'contexts': contexts,
        'ground_truth': ground_truths
    })

    # Evaluate
    result = evaluate(
        dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_recall,
            context_precision
        ]
    )

    # Assert minimum thresholds
    assert result['faithfulness'] > 0.8, "Faithfulness too low"
    assert result['answer_relevancy'] > 0.7, "Answer relevancy too low"
    assert result['context_recall'] > 0.6, "Context recall too low"

    print(f"\nRAGAS Scores:")
    print(f"  Faithfulness: {result['faithfulness']:.3f}")
    print(f"  Answer Relevancy: {result['answer_relevancy']:.3f}")
    print(f"  Context Recall: {result['context_recall']:.3f}")
    print(f"  Context Precision: {result['context_precision']:.3f}")
```

---

## 8. Maintaining the Dataset

### Regular Update Schedule

| Frequency | Task | Who |
|-----------|------|-----|
| Weekly | Review failed production queries | Developer |
| Monthly | Add new test cases from user logs | Developer + Installer |
| Quarterly | Full dataset review and cleanup | Team |
| Yearly | Major revision with new categories | Team + Stakeholders |

### Adding New Test Cases

When you find a query that the system handled poorly:

1. **Log the failure**
```python
# In app.py
if min_distance > DISTANCE_THRESHOLD:
    log_failed_query(query, min_distance, results)
```

2. **Review and extract**
```bash
# Review failed queries
cat logs/failed_queries.jsonl | jq -r '.query'
```

3. **Create test case**
```json
{
    "id": "new-case-001",
    "query": "[extracted from logs]",
    "category": "[determined by analysis]",
    "expected_docs": ["[identified correct docs]"],
    "expected_answer_contains": ["[key terms]"],
    "reference_answer": "[written by expert]",
    "difficulty": "medium",
    "tags": ["[relevant tags]"],
    "notes": "Added from production failure on 2024-12-15"
}
```

4. **Validate with installer**
- Review reference answer
- Verify expected docs are correct
- Confirm difficulty rating

5. **Add to dataset**
```bash
# Edit golden dataset
vi tests/golden_dataset.json

# Run tests to verify
pytest tests/test_rag_evaluation.py::test_answer_contains_keywords[new-case-001]

# Update changelog
vi tests/golden_dataset_CHANGELOG.md

# Commit
git add tests/golden_dataset.json tests/golden_dataset_CHANGELOG.md
git commit -m "test: add new-case-001 for printer issue"
```

### Removing Outdated Test Cases

Test cases become outdated when:
- Documentation changes and old query no longer valid
- SQL schema changes
- Category classification changes
- Duplicate of another test case

**Process:**

1. **Mark as deprecated** (don't delete immediately)
```json
{
    "id": "old-case-001",
    "query": "...",
    "deprecated": true,
    "deprecated_date": "2024-12-15",
    "deprecated_reason": "Replaced by new-case-005 with better phrasing",
    "replacement_id": "new-case-005"
}
```

2. **Wait one version cycle** (e.g., keep in v1.2.0, remove in v1.3.0)

3. **Remove from dataset**
```bash
# Remove from JSON
vi tests/golden_dataset.json

# Update changelog
vi tests/golden_dataset_CHANGELOG.md

# Commit
git commit -m "test: remove deprecated old-case-001 (replaced by new-case-005)"
```

### Tracking Dataset Health

Create a dashboard to monitor dataset quality over time.

**Script: `tests/dataset_health.py`**

```python
"""
Track golden dataset health metrics over time
"""

import json
from collections import Counter
from datetime import datetime

def analyze_dataset_health(dataset_path='tests/golden_dataset.json'):
    """Generate health report for golden dataset"""

    with open(dataset_path) as f:
        data = json.load(f)

    test_cases = data['test_cases']

    # Basic stats
    print("GOLDEN DATASET HEALTH REPORT")
    print("=" * 60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Dataset version: {data['metadata']['version']}")
    print(f"Total test cases: {len(test_cases)}\n")

    # Category distribution
    categories = Counter(tc['category'] for tc in test_cases)
    print("Category Distribution:")
    for category, count in categories.most_common():
        percentage = count / len(test_cases) * 100
        bar = '█' * int(percentage / 2)
        print(f"  {category:12s} {count:3d} ({percentage:5.1f}%) {bar}")

    # Difficulty distribution
    difficulties = Counter(tc['difficulty'] for tc in test_cases)
    print("\nDifficulty Distribution:")
    for difficulty in ['easy', 'medium', 'hard']:
        count = difficulties[difficulty]
        percentage = count / len(test_cases) * 100
        bar = '█' * int(percentage / 2)
        print(f"  {difficulty:12s} {count:3d} ({percentage:5.1f}%) {bar}")

    # Tag analysis
    all_tags = []
    for tc in test_cases:
        all_tags.extend(tc.get('tags', []))
    tag_counts = Counter(all_tags)
    print("\nTop 10 Tags:")
    for tag, count in tag_counts.most_common(10):
        print(f"  {tag:20s} {count:3d}")

    # Coverage gaps
    print("\nCoverage Analysis:")

    # Check for minimum per category
    min_per_category = 3
    undercovered = [cat for cat, count in categories.items() if count < min_per_category]
    if undercovered:
        print(f"  ⚠ Categories with < {min_per_category} test cases: {', '.join(undercovered)}")
    else:
        print(f"  ✓ All categories have >= {min_per_category} test cases")

    # Check difficulty balance
    easy_ratio = difficulties['easy'] / len(test_cases)
    if easy_ratio > 0.5:
        print(f"  ⚠ Too many easy test cases ({easy_ratio*100:.1f}%), add more medium/hard")
    elif easy_ratio < 0.3:
        print(f"  ⚠ Too few easy test cases ({easy_ratio*100:.1f}%), add more basic cases")
    else:
        print(f"  ✓ Good difficulty balance")

    # Check for missing fields
    missing_notes = sum(1 for tc in test_cases if not tc.get('notes'))
    if missing_notes > len(test_cases) * 0.5:
        print(f"  ⚠ {missing_notes} test cases missing notes field")

    print("\n" + "=" * 60)

if __name__ == '__main__':
    analyze_dataset_health()
```

**Run monthly:**
```bash
python tests/dataset_health.py > logs/dataset_health_$(date +%Y%m%d).txt
```

### CHANGELOG Template

Keep a detailed changelog for all dataset modifications.

**File: `tests/golden_dataset_CHANGELOG.md`**

```markdown
# Golden Dataset Changelog

All notable changes to the golden test dataset will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Nothing yet

### Changed
- Nothing yet

### Removed
- Nothing yet

## [1.2.0] - 2024-04-20

### Added
- 8 new test cases for menu modifiers (menu-003 through menu-010)
- `min_faithfulness` and `min_answer_relevancy` fields to all test cases
- Related test IDs to link similar cases

### Changed
- Updated printer-002 reference answer to include PrintGroup troubleshooting steps
- Increased difficulty of payment-002 from "medium" to "hard"
- Reorganized tags for better searchability

### Removed
- Deprecated order-003 (replaced by order-005 with clearer phrasing)

## [1.1.0] - 2024-03-15

### Added
- 5 new payment test cases (payment-003 through payment-007)
- Graded relevance scores for all expected docs
- `notes` field explaining edge cases
- `should_trigger_followup` field for testing follow-up question flow

### Changed
- Updated all printer test cases with hardware troubleshooting steps
- Standardized SQL query formatting in reference answers
- Improved category keywords for better detection

### Removed
- Removed test case void-004 (duplicate of void-001)

## [1.0.0] - 2024-12-10

### Added
- Initial golden dataset with 15 test cases
- Coverage across all 6 categories (printer, payment, employee, order, menu, cash)
- Difficulty ratings (easy, medium, hard)
- Basic structure: id, query, expected_docs, expected_answer_contains, reference_answer
- Validation by HungerRush installer team

### Notes
- Baseline for RAG evaluation
- Test cases extracted from `sql_reference.md` and installer interviews
```

### Version Bumping Rules

Follow semantic versioning:

- **Major version (2.0.0)**: Breaking changes to dataset structure
  - Example: Changing `expected_docs` from array to object
  - Example: Removing required fields

- **Minor version (1.1.0)**: Backward-compatible additions
  - Example: Adding new test cases
  - Example: Adding optional fields

- **Patch version (1.0.1)**: Backward-compatible fixes
  - Example: Fixing typos in reference answers
  - Example: Correcting expected keywords

### Archive Old Versions

Keep historical versions for comparison:

```
tests/
├── golden_dataset.json           # Current version
├── archive/
│   ├── golden_dataset_v1.0.0.json
│   ├── golden_dataset_v1.1.0.json
│   └── golden_dataset_v1.2.0.json
└── golden_dataset_CHANGELOG.md
```

**Script to archive:**

```bash
#!/bin/bash
# archive_dataset.sh

VERSION=$(jq -r '.metadata.version' tests/golden_dataset.json)
ARCHIVE_PATH="tests/archive/golden_dataset_v${VERSION}.json"

echo "Archiving dataset version ${VERSION} to ${ARCHIVE_PATH}"
cp tests/golden_dataset.json "${ARCHIVE_PATH}"
git add "${ARCHIVE_PATH}"
git commit -m "archive: save golden dataset v${VERSION}"
```

---

## Summary

A well-maintained golden dataset is the foundation of reliable RAG evaluation. Follow this guide to:

1. **Start small** - Begin with 15-20 high-quality test cases covering core use cases
2. **Grow strategically** - Add cases from real user queries and installer feedback
3. **Maintain rigorously** - Regular reviews, clear changelog, version control
4. **Measure continuously** - Run automated tests on every code change

For Escalation Helper, aim to:
- Maintain 50+ test cases covering all 6 categories
- Achieve 85%+ pass rate on golden dataset
- Review and update dataset monthly
- Use RAGAS metrics for objective quality measurement

The effort invested in creating and maintaining your golden dataset will pay dividends in RAG quality, debugging efficiency, and user satisfaction.
