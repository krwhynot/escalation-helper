# Testing Frameworks Comparison for RAG Systems

## 1. RAGAS (PRIMARY RECOMMENDATION)

### Overview
- Open-source RAG evaluation framework
- "Gold standard" for RAG testing in 2025
- LLM-as-judge approach (no human annotations needed)
- Integrates with LangChain, LlamaIndex, and standalone applications

### Installation
```bash
pip install ragas
```

### Core Metrics

#### Faithfulness
Measures whether the generated answer is factually consistent with the retrieved contexts. Score ranges from 0 to 1 (higher is better).

#### Answer Relevancy
Evaluates how relevant the generated answer is to the user's question. Penalizes incomplete or redundant information.

#### Context Recall
Measures whether all relevant information from the ground truth is present in the retrieved contexts. Requires reference answers.

#### Context Precision
Evaluates whether the most relevant contexts are ranked higher. Measures the quality of retrieval ranking.

#### Factual Correctness
Compares the generated answer against a reference answer to measure factual accuracy.

### Complete Example for Escalation Helper

```python
from ragas import evaluate, EvaluationDataset
from ragas.metrics import Faithfulness, LLMContextRecall, FactualCorrectness
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI

# Setup evaluator LLM
llm = ChatOpenAI(model="gpt-4o-mini")
evaluator_llm = LangchainLLMWrapper(llm)

# Prepare test data
test_cases = [
    {
        "user_input": "cashier can't void an order",
        "retrieved_contexts": [
            "Check SecGrp table for void permissions...",
            "Verify employee has VoidItem permission enabled...",
            "SQL: SELECT * FROM SecGrp WHERE PermissionName LIKE '%Void%'"
        ],
        "response": "To fix void issues, check the SecGrp table for void permissions. Run this SQL: SELECT * FROM SecGrp WHERE PermissionName LIKE '%Void%'",
        "reference": "The SecGrp table controls void permissions. Check if the employee's security group has VoidItem permission enabled."
    },
    {
        "user_input": "receipt printer not printing",
        "retrieved_contexts": [
            "Check Printer table for device configuration...",
            "Verify PrinterType matches hardware model...",
            "SQL: SELECT * FROM Printer WHERE StationID = ?"
        ],
        "response": "Check the Printer table configuration using: SELECT * FROM Printer WHERE StationID = ?. Verify PrinterType matches your hardware.",
        "reference": "Printer issues are usually in the Printer table. Check PrinterType, Port, and Enabled columns."
    }
]

# Create evaluation dataset
dataset = EvaluationDataset.from_list(test_cases)

# Evaluate with multiple metrics
result = evaluate(
    dataset=dataset,
    metrics=[
        Faithfulness(),
        LLMContextRecall(),
        FactualCorrectness()
    ],
    llm=evaluator_llm
)

# View results
print(result)
# Output example:
# {
#   'faithfulness': 0.95,
#   'context_recall': 0.88,
#   'factual_correctness': 0.82
# }

# Access detailed per-sample results
for idx, row in enumerate(result.to_pandas().itertuples()):
    print(f"Test Case {idx + 1}:")
    print(f"  Faithfulness: {row.faithfulness:.2f}")
    print(f"  Context Recall: {row.context_recall:.2f}")
    print(f"  Factual Correctness: {row.factual_correctness:.2f}")
```

### Integration with Escalation Helper

```python
# integration_example.py
from ragas import evaluate, EvaluationDataset
from ragas.metrics import Faithfulness, AnswerRelevancy
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI
import app  # Your Escalation Helper app
import config

def evaluate_escalation_helper(test_queries):
    """
    Evaluate Escalation Helper using RAGAS metrics.

    Args:
        test_queries: List of dicts with 'query' and 'reference' keys

    Returns:
        RAGAS evaluation results
    """
    llm = ChatOpenAI(model=config.LLM_MODEL)
    evaluator_llm = LangchainLLMWrapper(llm)

    test_cases = []

    for test in test_queries:
        query = test['query']

        # Get results from your app
        results = app.search_knowledge_base(query)

        # Extract contexts and response
        contexts = [r['content'] for r in results]
        response = app.generate_response(query, results)

        test_cases.append({
            "user_input": query,
            "retrieved_contexts": contexts,
            "response": response,
            "reference": test.get('reference', '')  # Optional
        })

    dataset = EvaluationDataset.from_list(test_cases)

    # Evaluate
    result = evaluate(
        dataset=dataset,
        metrics=[Faithfulness(), AnswerRelevancy()],
        llm=evaluator_llm
    )

    return result

# Example usage
test_queries = [
    {
        "query": "cashier can't void an order",
        "reference": "Check SecGrp table void permissions"
    },
    {
        "query": "receipt printer not working",
        "reference": "Verify Printer table configuration"
    }
]

results = evaluate_escalation_helper(test_queries)
print(f"Average Faithfulness: {results['faithfulness']:.2f}")
print(f"Average Answer Relevancy: {results['answer_relevancy']:.2f}")
```

### Async Evaluation for Speed

```python
import asyncio
from ragas import evaluate
from ragas.metrics import Faithfulness

async def evaluate_async(dataset):
    """Run RAGAS evaluation asynchronously for better performance."""
    result = await evaluate(
        dataset=dataset,
        metrics=[Faithfulness()],
        llm=evaluator_llm,
        show_progress=True
    )
    return result

# Use in async context
# results = asyncio.run(evaluate_async(dataset))
```

### Pros
- **RAG-specific metrics** designed for retrieval-augmented generation use cases
- **Lower cost** than alternatives (fewer LLM API calls per evaluation)
- **Active development** and strong community support (40k+ GitHub stars)
- **Good documentation** with examples for common frameworks
- **No manual labeling** required for most metrics
- **Easy integration** with existing Python codebases

### Cons
- **Requires LLM API access** (OpenAI or compatible) for evaluation
- **Can be slow** for large datasets without async evaluation
- **Some metrics require reference answers** (Context Recall, Factual Correctness)
- **LLM-as-judge limitations** (inherits biases from evaluator LLM)
- **Cost scales** with number of test cases and metric complexity

### Best Practices

1. **Start with Faithfulness + Answer Relevancy**
   - These don't require reference answers
   - Good baseline for RAG quality

2. **Use async evaluation for speed**
   ```python
   result = await evaluate(dataset, metrics, llm, show_progress=True)
   ```

3. **Cache embeddings when possible**
   - Store test embeddings to avoid recomputation
   - Speeds up repeated evaluations

4. **Run on representative sample first**
   - Test 10-20 cases before scaling to full dataset
   - Validate metric behavior matches expectations

5. **Monitor metric trends over time**
   - Track scores across versions
   - Set minimum thresholds for CI/CD

6. **Use GPT-4 for evaluation, not GPT-3.5**
   - Better judgment quality
   - Worth the extra cost for accurate evaluation

---

## 2. DeepEval

### What it is
- "Pytest for LLMs" - unit test interface for LLM applications
- 14+ metrics including RAG-specific, safety, and bias metrics
- Built-in synthetic data generation (Synthesizer)
- Confidence intervals for statistical significance

### When to Consider
- **Need synthetic test data generation** - Automatically create test cases from documents
- **Want pytest-style test interface** - Familiar testing workflow for Python developers
- **Need safety/toxicity testing** - Built-in metrics for harmful content detection
- **Require statistical confidence** - Confidence intervals for metric reliability

### Installation
```bash
pip install deepeval
```

### Basic Example
```python
from deepeval import assert_test
from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

def test_escalation_helper():
    test_case = LLMTestCase(
        input="cashier can't void an order",
        actual_output="Check SecGrp table for void permissions...",
        retrieval_context=["SecGrp controls permissions..."]
    )

    faithfulness_metric = FaithfulnessMetric(threshold=0.7)
    assert_test(test_case, [faithfulness_metric])
```

### Key Difference from RAGAS
- **More comprehensive** - Includes safety, bias, toxicity testing beyond RAG
- **Steeper learning curve** - More configuration options and complexity
- **Higher API costs** - More LLM calls per evaluation for detailed metrics
- **Pytest integration** - Natural fit for Python testing workflows
- **Synthetic data** - Can generate test cases automatically

---

## 3. TruLens

### What it is
- Focus on **explainability and tracing** for LLM applications
- Feedback functions for custom evaluation logic
- Real-time monitoring and observability
- Developed by Stanford professors (founded by Jerry Liu)

### When to Consider
- **Need detailed audit trails** - Comprehensive logging of every decision
- **Regulatory/compliance requirements** - Explain why specific answers were generated
- **Want to understand WHY scores change** - Deep introspection into model behavior
- **Production monitoring** - Real-time performance tracking

### Installation
```bash
pip install trulens
```

### Basic Example
```python
from trulens_eval import Feedback, TruChain
from trulens_eval.feedback import Groundedness

# Define feedback functions
f_groundedness = Feedback(Groundedness().groundedness_measure).on_output()

# Wrap your application
tru_app = TruChain(
    your_chain,
    app_id="escalation-helper",
    feedbacks=[f_groundedness]
)

# Use wrapped app
with tru_app as recording:
    result = tru_app.app("cashier can't void an order")
```

### Key Difference from RAGAS
- **Better explainability** - Detailed traces showing reasoning
- **More engineering effort** - Requires wrapping application logic
- **Declined activity** - Less active development after Snowflake acquisition (2024)
- **Production focus** - Better for monitoring than one-off evaluations
- **Custom feedback** - Flexible framework for custom metrics

---

## 4. LangSmith

### What it is
- LangChain's official observability and evaluation platform
- Built-in tracing and debugging for LangChain applications
- Dataset management and versioning
- Human feedback collection and annotation tools

### When to Consider
- **Already using LangChain** - Seamless integration with existing code
- **Need production monitoring** - Real-time observability and alerting
- **Want integrated tracing + evaluation** - Single platform for both
- **Team collaboration** - Share datasets and evaluations across team

### Installation
```bash
pip install langsmith
```

### Basic Example
```python
from langsmith import Client
from langchain.chat_models import ChatOpenAI

client = Client()

# Create dataset
dataset = client.create_dataset("escalation-helper-tests")
client.create_examples(
    dataset_id=dataset.id,
    examples=[
        {"input": "cashier can't void", "output": "Check SecGrp..."}
    ]
)

# Evaluate
def predict(input_dict):
    return {"output": your_app.run(input_dict["input"])}

client.run_on_dataset(
    dataset_name="escalation-helper-tests",
    llm_or_chain_factory=predict
)
```

### Key Difference from RAGAS
- **Platform vs library** - Web UI + API vs pure Python library
- **Requires LangChain ecosystem** - Best if already using LangChain
- **Paid tiers for advanced features** - Free tier available but limited
- **Better collaboration** - Team features, shared datasets
- **Production-ready** - Built for ongoing monitoring, not just testing

---

## 5. Comparison Table

| Feature | RAGAS | DeepEval | TruLens | LangSmith |
|---------|-------|----------|---------|-----------|
| **Primary Focus** | RAG evaluation metrics | LLM unit testing | Explainability & tracing | Observability platform |
| **Setup Effort** | Low | Medium | Medium | Low (if using LangChain) |
| **Cost** | Low | Medium | Low | Free tier + paid plans |
| **RAG Metrics** | Excellent | Good | Good | Good |
| **Safety Testing** | No | Yes | No | Limited |
| **Synthetic Data** | Yes (limited) | Yes (advanced) | No | No |
| **Tracing** | No | Limited | Excellent | Excellent |
| **Pytest Integration** | No | Yes | No | No |
| **Production Monitoring** | No | Limited | Yes | Yes |
| **Open Source** | Yes | Yes | Yes | Partially |
| **LLM Required** | Yes | Yes | Yes | Yes |
| **Best For** | RAG evaluation | Comprehensive testing | Audit trails | LangChain users |
| **Community** | Active (40k stars) | Growing (3k stars) | Declining | Active (LangChain) |
| **Documentation** | Excellent | Good | Good | Excellent |

---

## 6. Recommendation for Escalation Helper

### Use RAGAS as Primary Framework

**Why RAGAS is the best choice:**

1. **Purpose-built for RAG evaluation**
   - Metrics designed specifically for retrieval-augmented generation
   - Faithfulness and Context Recall directly measure what matters

2. **Low setup effort**
   - Simple pip install
   - Works with your existing code without major refactoring
   - No need to wrap application logic

3. **Cost-effective**
   - Fewer LLM API calls per evaluation
   - Can use GPT-4o-mini for most metrics
   - No platform fees or subscriptions

4. **Metrics match our needs**
   - **Faithfulness** - Ensures SQL queries are grounded in documentation
   - **Context Recall** - Verifies retrieval finds relevant docs
   - **Answer Relevancy** - Measures response quality

5. **Active community and development**
   - Regular updates and new features
   - Strong GitHub activity (40k+ stars)
   - Good documentation and examples

### Implementation Path

**Phase 1: Basic Evaluation (Week 1)**
- Install RAGAS
- Create 10-20 test cases covering common queries
- Evaluate with Faithfulness + Answer Relevancy
- Set baseline scores

**Phase 2: Expand Coverage (Week 2-3)**
- Add test cases for edge cases
- Include Context Recall with reference answers
- Automate evaluation in CI/CD

**Phase 3: Continuous Monitoring (Ongoing)**
- Track metric trends over time
- Set minimum thresholds (e.g., Faithfulness > 0.85)
- Add regression tests for bugs

### Consider Adding Later

**LangSmith if you need:**
- Production monitoring and alerting
- Team collaboration on datasets
- Real-time performance tracking
- Already migrating to LangChain

**DeepEval if you need:**
- Synthetic test data generation
- Safety/toxicity testing
- Pytest-style test workflow
- Statistical confidence intervals

**TruLens if you need:**
- Regulatory compliance with audit trails
- Deep explainability for debugging
- Custom feedback functions
- Production observability

---

## 7. Getting Started with RAGAS

### Step 1: Install Dependencies

```bash
pip install ragas langchain-openai
```

### Step 2: Create Test Dataset

Create `tests/ragas_test_cases.json`:

```json
[
  {
    "user_input": "cashier can't void an order",
    "retrieved_contexts": [
      "Check SecGrp table for void permissions",
      "SQL: SELECT * FROM SecGrp WHERE PermissionName LIKE '%Void%'"
    ],
    "response": "To fix void issues, check the SecGrp table...",
    "reference": "SecGrp table controls void permissions"
  }
]
```

### Step 3: Run Evaluation

Create `tests/test_ragas.py`:

```python
import json
from ragas import evaluate, EvaluationDataset
from ragas.metrics import Faithfulness, AnswerRelevancy
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI

# Load test cases
with open('tests/ragas_test_cases.json') as f:
    test_cases = json.load(f)

# Setup
llm = ChatOpenAI(model="gpt-4o-mini")
evaluator_llm = LangchainLLMWrapper(llm)

# Evaluate
dataset = EvaluationDataset.from_list(test_cases)
result = evaluate(
    dataset=dataset,
    metrics=[Faithfulness(), AnswerRelevancy()],
    llm=evaluator_llm
)

print(f"Faithfulness: {result['faithfulness']:.2f}")
print(f"Answer Relevancy: {result['answer_relevancy']:.2f}")

# Assert minimum thresholds
assert result['faithfulness'] >= 0.85, "Faithfulness below threshold"
assert result['answer_relevancy'] >= 0.80, "Relevancy below threshold"
```

### Step 4: Run Tests

```bash
python tests/test_ragas.py
```

---

## 8. Additional Resources

### RAGAS
- Documentation: https://docs.ragas.io/
- GitHub: https://github.com/explodinggradients/ragas
- Tutorials: https://docs.ragas.io/en/stable/getstarted/

### DeepEval
- Documentation: https://docs.confident-ai.com/
- GitHub: https://github.com/confident-ai/deepeval

### TruLens
- Documentation: https://www.trulens.org/
- GitHub: https://github.com/truera/trulens

### LangSmith
- Documentation: https://docs.smith.langchain.com/
- Platform: https://smith.langchain.com/
