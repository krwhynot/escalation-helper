# RAG Metrics Deep Dive

This guide covers comprehensive metrics for evaluating RAG (Retrieval-Augmented Generation) systems like Escalation Helper, an AI-powered SQL troubleshooting assistant.

## Table of Contents
1. [Retrieval Metrics](#1-retrieval-metrics)
2. [Generation Metrics (RAGAS)](#2-generation-metrics-ragas)
3. [Metric Selection Guide](#3-metric-selection-guide)
4. [Recommended Thresholds](#4-recommended-thresholds)
5. [Implementation Examples](#5-implementation-examples)

---

## 1. Retrieval Metrics

Retrieval metrics evaluate how well the system finds relevant documents before generation.

### Precision@K

**What it measures**: Of the K documents retrieved, how many are actually relevant?

**Formula**:
```
Precision@K = (Number of relevant docs in top K) / K
```

**Example**:
- System retrieves 5 documents (K=5)
- 3 of those documents are relevant to the query
- Precision@5 = 3/5 = 0.6 (60%)

**When to use**:
- When you care about result quality over completeness
- When showing irrelevant results has a cost (user frustration, wasted API calls)
- For Escalation Helper: Ensuring SQL queries shown are actually applicable

**Strengths**:
- Easy to understand and compute
- Directly measures what users see

**Weaknesses**:
- Doesn't account for total number of relevant documents
- Doesn't consider ranking order

**Code example**:
```python
def precision_at_k(retrieved_docs, relevant_docs, k):
    """
    Calculate Precision@K

    Args:
        retrieved_docs: List of retrieved document IDs in rank order
        relevant_docs: Set of relevant document IDs for this query
        k: Number of top results to consider

    Returns:
        float: Precision score between 0 and 1
    """
    retrieved_k = retrieved_docs[:k]
    relevant_count = sum(1 for doc in retrieved_k if doc in relevant_docs)
    return relevant_count / k

# Example usage
retrieved = ['doc1', 'doc2', 'doc3', 'doc4', 'doc5']
relevant = {'doc1', 'doc3', 'doc5', 'doc7', 'doc9'}

print(f"Precision@3: {precision_at_k(retrieved, relevant, 3)}")  # 2/3 = 0.667
print(f"Precision@5: {precision_at_k(retrieved, relevant, 5)}")  # 3/5 = 0.600
```

---

### Recall@K

**What it measures**: Of all relevant documents in the corpus, how many did we retrieve in the top K results?

**Formula**:
```
Recall@K = (Number of relevant docs in top K) / (Total number of relevant docs)
```

**Example**:
- 10 relevant documents exist in the database
- System retrieves 7 of them in top K results
- Recall@K = 7/10 = 0.7 (70%)

**When to use**:
- When missing relevant documents is costly
- When completeness matters more than precision
- For Escalation Helper: Ensuring we don't miss critical SQL fixes

**Strengths**:
- Measures completeness of retrieval
- Important for comprehensive troubleshooting

**Weaknesses**:
- Requires knowing ALL relevant documents (ground truth)
- Doesn't penalize irrelevant results

**Code example**:
```python
def recall_at_k(retrieved_docs, relevant_docs, k):
    """
    Calculate Recall@K

    Args:
        retrieved_docs: List of retrieved document IDs in rank order
        relevant_docs: Set of all relevant document IDs for this query
        k: Number of top results to consider

    Returns:
        float: Recall score between 0 and 1
    """
    if len(relevant_docs) == 0:
        return 0.0

    retrieved_k = set(retrieved_docs[:k])
    relevant_count = len(retrieved_k.intersection(relevant_docs))
    return relevant_count / len(relevant_docs)

# Example usage
retrieved = ['doc1', 'doc2', 'doc3', 'doc4', 'doc5']
relevant = {'doc1', 'doc3', 'doc5', 'doc7', 'doc9'}

print(f"Recall@3: {recall_at_k(retrieved, relevant, 3)}")  # 2/5 = 0.400
print(f"Recall@5: {recall_at_k(retrieved, relevant, 5)}")  # 3/5 = 0.600
```

---

### F1@K Score

**What it measures**: Harmonic mean of Precision@K and Recall@K, balancing both metrics.

**Formula**:
```
F1@K = 2 × (Precision@K × Recall@K) / (Precision@K + Recall@K)
```

**When to use**:
- When you need a single metric balancing quality and completeness
- For overall system evaluation

**Code example**:
```python
def f1_at_k(retrieved_docs, relevant_docs, k):
    """Calculate F1@K score"""
    precision = precision_at_k(retrieved_docs, relevant_docs, k)
    recall = recall_at_k(retrieved_docs, relevant_docs, k)

    if precision + recall == 0:
        return 0.0

    return 2 * (precision * recall) / (precision + recall)

# Example usage
retrieved = ['doc1', 'doc2', 'doc3', 'doc4', 'doc5']
relevant = {'doc1', 'doc3', 'doc5', 'doc7', 'doc9'}

print(f"F1@5: {f1_at_k(retrieved, relevant, 5)}")  # 0.600
```

---

### Mean Reciprocal Rank (MRR)

**What it measures**: How high is the first relevant result in the ranking?

**Formula**:
```
MRR = Average of (1 / rank of first relevant document)
```

**Example**:
- Query 1: First relevant doc at rank 2 → score = 1/2 = 0.5
- Query 2: First relevant doc at rank 1 → score = 1/1 = 1.0
- Query 3: First relevant doc at rank 3 → score = 1/3 = 0.333
- MRR = (0.5 + 1.0 + 0.333) / 3 = 0.611

**When to use**:
- When users typically only look at top results
- For single-answer queries (one best SQL query)
- For Escalation Helper: Critical since users often need one specific fix

**Strengths**:
- Emphasizes top-ranked results
- Simple to interpret

**Weaknesses**:
- Only considers first relevant result
- Doesn't account for other relevant documents

**Code example**:
```python
def reciprocal_rank(retrieved_docs, relevant_docs):
    """
    Calculate Reciprocal Rank for a single query

    Returns:
        float: 1/rank of first relevant doc, or 0 if none found
    """
    for rank, doc in enumerate(retrieved_docs, start=1):
        if doc in relevant_docs:
            return 1.0 / rank
    return 0.0

def mean_reciprocal_rank(queries_results):
    """
    Calculate Mean Reciprocal Rank across multiple queries

    Args:
        queries_results: List of tuples (retrieved_docs, relevant_docs)

    Returns:
        float: MRR score
    """
    rr_scores = [
        reciprocal_rank(retrieved, relevant)
        for retrieved, relevant in queries_results
    ]
    return sum(rr_scores) / len(rr_scores) if rr_scores else 0.0

# Example usage
queries = [
    (['doc2', 'doc1', 'doc3'], {'doc1', 'doc5'}),  # First relevant at rank 2
    (['doc1', 'doc2', 'doc3'], {'doc1', 'doc5'}),  # First relevant at rank 1
    (['doc1', 'doc2', 'doc3'], {'doc3', 'doc5'}),  # First relevant at rank 3
]

mrr = mean_reciprocal_rank(queries)
print(f"MRR: {mrr:.3f}")  # 0.611
```

---

### Normalized Discounted Cumulative Gain (NDCG)

**What it measures**: Quality of ranking considering both relevance and position, with higher positions weighted more heavily.

**How it works**:
1. Assign relevance scores to documents (e.g., 0=not relevant, 1=somewhat, 2=very relevant)
2. Calculate Discounted Cumulative Gain (DCG): sum of (relevance / log2(rank + 1))
3. Calculate Ideal DCG (IDCG): DCG if documents were perfectly ranked
4. NDCG = DCG / IDCG

**Formula**:
```
DCG@K = Σ(relevance_i / log2(i + 1)) for i=1 to K
NDCG@K = DCG@K / IDCG@K
```

**When to use**:
- When you have graded relevance (not just binary relevant/irrelevant)
- When ranking quality matters
- When some results are more relevant than others

**Strengths**:
- Considers both relevance and ranking
- Supports multi-level relevance judgments
- Industry standard for ranking evaluation

**Weaknesses**:
- More complex to compute
- Requires graded relevance annotations

**Code example**:
```python
import numpy as np

def dcg_at_k(relevances, k):
    """
    Calculate Discounted Cumulative Gain at K

    Args:
        relevances: List of relevance scores in retrieved order
        k: Number of results to consider

    Returns:
        float: DCG score
    """
    relevances = np.array(relevances[:k])
    if relevances.size == 0:
        return 0.0

    # Discount factor: 1/log2(rank + 1)
    discounts = np.log2(np.arange(2, relevances.size + 2))
    return np.sum(relevances / discounts)

def ndcg_at_k(relevances, k):
    """
    Calculate Normalized Discounted Cumulative Gain at K

    Args:
        relevances: List of relevance scores in retrieved order
        k: Number of results to consider

    Returns:
        float: NDCG score between 0 and 1
    """
    dcg = dcg_at_k(relevances, k)

    # IDCG: DCG if items were perfectly sorted by relevance
    ideal_relevances = sorted(relevances, reverse=True)
    idcg = dcg_at_k(ideal_relevances, k)

    if idcg == 0:
        return 0.0

    return dcg / idcg

# Example usage
# Relevance scores: 2=highly relevant, 1=somewhat relevant, 0=not relevant
retrieved_relevances = [2, 0, 1, 2, 0]  # Actual retrieval order
ideal_relevances = [2, 2, 1, 0, 0]      # Perfect ranking

print(f"DCG@5: {dcg_at_k(retrieved_relevances, 5):.3f}")
print(f"NDCG@5: {ndcg_at_k(retrieved_relevances, 5):.3f}")

# For Escalation Helper example
def evaluate_sql_retrieval(retrieved_queries, relevance_scores):
    """
    Evaluate SQL query retrieval

    Args:
        retrieved_queries: List of retrieved SQL query IDs
        relevance_scores: Dict mapping query_id to relevance (0-2)
    """
    relevances = [relevance_scores.get(qid, 0) for qid in retrieved_queries]

    return {
        'NDCG@3': ndcg_at_k(relevances, 3),
        'NDCG@5': ndcg_at_k(relevances, 5),
        'DCG@3': dcg_at_k(relevances, 3),
    }
```

---

### Hit Rate (Success Rate)

**What it measures**: Was at least one relevant document retrieved in the top K results?

**Formula**:
```
Hit Rate = (Queries with ≥1 relevant doc in top K) / (Total queries)
```

**Example**:
- 100 test queries
- 85 queries have at least one relevant doc in top 5
- Hit Rate@5 = 85/100 = 0.85

**When to use**:
- Simple baseline metric
- When any relevant result is acceptable
- Quick system health check

**Code example**:
```python
def hit_rate_at_k(queries_results, k):
    """
    Calculate Hit Rate@K across multiple queries

    Args:
        queries_results: List of tuples (retrieved_docs, relevant_docs)
        k: Number of top results to consider

    Returns:
        float: Hit rate between 0 and 1
    """
    hits = 0
    for retrieved, relevant in queries_results:
        retrieved_k = set(retrieved[:k])
        if retrieved_k.intersection(relevant):
            hits += 1

    return hits / len(queries_results) if queries_results else 0.0

# Example usage
queries = [
    (['doc1', 'doc2', 'doc3'], {'doc1', 'doc5'}),  # Hit
    (['doc1', 'doc2', 'doc3'], {'doc4', 'doc5'}),  # Miss
    (['doc1', 'doc2', 'doc3'], {'doc3', 'doc5'}),  # Hit
]

hit_rate = hit_rate_at_k(queries, k=3)
print(f"Hit Rate@3: {hit_rate:.3f}")  # 0.667
```

---

## 2. Generation Metrics (RAGAS)

RAGAS (Retrieval-Augmented Generation Assessment) provides LLM-based metrics for evaluating the quality of generated responses.

### Installation

```bash
pip install ragas
pip install langchain-openai
```

### Faithfulness

**What it measures**: Are all claims in the response supported by the retrieved context? This prevents hallucinations.

**Formula**:
```
Faithfulness = (Number of claims supported by context) / (Total number of claims)
```

**Score range**: 0 to 1 (higher is better)

**How RAGAS calculates it**:
1. Extract atomic claims from the generated response using LLM
2. For each claim, check if it's supported by retrieved context
3. Calculate ratio of supported claims

**Why it matters for Escalation Helper**:
- SQL queries MUST come from documentation
- Hallucinated SQL could break customer databases
- Critical for trust and accuracy

**Code example**:
```python
from ragas.metrics import Faithfulness
from ragas import evaluate
from datasets import Dataset
from langchain_openai import ChatOpenAI

# Initialize LLM for evaluation
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Initialize metric
faithfulness_metric = Faithfulness(llm=llm)

# Prepare evaluation data
data = {
    'user_input': [
        "How do I check if a cashier can void orders?"
    ],
    'response': [
        "You can check cashier permissions by querying the SecGrp table. "
        "Use: SELECT * FROM SecGrp WHERE SecGrpName = 'Cashier' to see "
        "the permission flags. The VoidOrder column indicates void permissions."
    ],
    'retrieved_contexts': [
        [
            "The SecGrp table controls user permissions. "
            "Each security group has permission flags like VoidOrder, RefundOrder, etc.",
            "To check permissions: SELECT * FROM SecGrp WHERE SecGrpName = 'Cashier'"
        ]
    ]
}

# Create dataset
dataset = Dataset.from_dict(data)

# Evaluate
result = evaluate(
    dataset,
    metrics=[faithfulness_metric]
)

print(f"Faithfulness Score: {result['faithfulness']:.3f}")

# For single sample evaluation
async def evaluate_single_response(query, response, contexts):
    """Evaluate faithfulness of a single response"""
    score = await faithfulness_metric.ascore(
        user_input=query,
        response=response,
        retrieved_contexts=contexts
    )
    return score

# Example usage in async context
import asyncio

async def main():
    score = await evaluate_single_response(
        query="How do I void an order?",
        response="Use SecGrp table to check permissions with SELECT * FROM SecGrp",
        contexts=["The SecGrp table controls permissions..."]
    )
    print(f"Score: {score:.3f}")

# asyncio.run(main())
```

---

### Answer Relevancy

**What it measures**: How well does the answer address the original question?

**How it works**:
1. Generate questions from the answer using LLM
2. Compare generated questions to original question
3. Calculate semantic similarity

**Score range**: 0 to 1 (higher is better)

**When to use**:
- Ensuring responses stay on topic
- Detecting overly verbose or tangential answers
- User satisfaction evaluation

**Code example**:
```python
from ragas.metrics import AnswerRelevancy
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Initialize
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embeddings = OpenAIEmbeddings()

answer_relevancy_metric = AnswerRelevancy(
    llm=llm,
    embeddings=embeddings
)

# Evaluation data
data = {
    'user_input': [
        "Why can't the cashier void orders?"
    ],
    'response': [
        "The cashier's void permission is controlled by the SecGrp table. "
        "Check the VoidOrder flag in their security group. "
        "If it's 0, they don't have permission."
    ],
    'retrieved_contexts': [
        [
            "SecGrp table controls permissions",
            "VoidOrder flag enables void capability"
        ]
    ]
}

dataset = Dataset.from_dict(data)

result = evaluate(
    dataset,
    metrics=[answer_relevancy_metric]
)

print(f"Answer Relevancy: {result['answer_relevancy']:.3f}")
```

---

### Context Recall

**What it measures**: Did we retrieve all the necessary information to answer the question?

**How it works**:
- Compare retrieved contexts to a reference answer
- Check if all facts in the reference answer are present in retrieved contexts

**Score range**: 0 to 1 (higher is better)

**When to use**:
- Evaluating retrieval completeness
- Ensuring critical information isn't missed
- For Escalation Helper: Verifying all relevant SQL queries are retrieved

**Code example**:
```python
from ragas.metrics import ContextRecall

context_recall_metric = ContextRecall(llm=llm)

# Requires ground truth reference answer
data = {
    'user_input': [
        "How do I check printer settings?"
    ],
    'retrieved_contexts': [
        [
            "Printer configuration is in the Printer table",
            "Use SELECT * FROM Printer WHERE PrinterID = @ID"
        ]
    ],
    'reference': [
        "Check the Printer table using SELECT * FROM Printer. "
        "Also verify PrinterQueue table for active print jobs."
    ]
}

dataset = Dataset.from_dict(data)

result = evaluate(
    dataset,
    metrics=[context_recall_metric]
)

print(f"Context Recall: {result['context_recall']:.3f}")
# Lower score indicates missing PrinterQueue information
```

---

### Context Precision

**What it measures**: Is the retrieved context actually useful for answering the question?

**How it works**:
- Checks if context chunks are relevant to the query
- Penalizes irrelevant context mixed with relevant context

**Score range**: 0 to 1 (higher is better)

**When to use**:
- Optimizing retrieval to reduce noise
- Improving context quality before generation
- Reducing LLM token usage

**Code example**:
```python
from ragas.metrics import ContextPrecision

context_precision_metric = ContextPrecision(llm=llm)

# Requires ground truth reference
data = {
    'user_input': [
        "How do I void an order?"
    ],
    'retrieved_contexts': [
        [
            "The SecGrp table controls void permissions",  # Relevant
            "Menu items are stored in MenuItem table",      # Not relevant
            "VoidOrder flag must be 1 for void access"      # Relevant
        ]
    ],
    'reference': [
        "Check SecGrp.VoidOrder permission flag"
    ]
}

dataset = Dataset.from_dict(data)

result = evaluate(
    dataset,
    metrics=[context_precision_metric]
)

print(f"Context Precision: {result['context_precision']:.3f}")
```

---

### Factual Correctness

**What it measures**: Is the generated answer factually accurate compared to ground truth?

**How it works**:
- Compare facts in generated answer to reference answer
- Use LLM to identify factual claims and verify accuracy

**Score range**: 0 to 1 (higher is better)

**Code example**:
```python
from ragas.metrics import FactualCorrectness

factual_correctness_metric = FactualCorrectness(llm=llm)

data = {
    'user_input': [
        "What table stores employee information?"
    ],
    'response': [
        "Employee information is stored in the Employee table. "
        "This includes employee ID, name, and security group assignment."
    ],
    'reference': [
        "The Employee table contains employee data including ID, name, "
        "and links to SecGrp for permissions."
    ],
    'retrieved_contexts': [
        ["The Employee table stores employee data..."]
    ]
}

dataset = Dataset.from_dict(data)

result = evaluate(
    dataset,
    metrics=[factual_correctness_metric]
)

print(f"Factual Correctness: {result['factual_correctness']:.3f}")
```

---

### Complete RAGAS Evaluation Example

```python
from ragas import evaluate
from ragas.metrics import (
    Faithfulness,
    AnswerRelevancy,
    ContextRecall,
    ContextPrecision,
    FactualCorrectness
)
from datasets import Dataset
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

def evaluate_escalation_helper(test_cases):
    """
    Comprehensive evaluation of Escalation Helper responses

    Args:
        test_cases: List of dicts with keys:
            - user_input: The question
            - response: Generated answer
            - retrieved_contexts: List of retrieved chunks
            - reference: Ground truth answer

    Returns:
        dict: Evaluation results for all metrics
    """
    # Initialize models
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embeddings = OpenAIEmbeddings()

    # Initialize metrics
    metrics = [
        Faithfulness(llm=llm),
        AnswerRelevancy(llm=llm, embeddings=embeddings),
        ContextRecall(llm=llm),
        ContextPrecision(llm=llm),
        FactualCorrectness(llm=llm)
    ]

    # Create dataset
    dataset = Dataset.from_dict({
        'user_input': [tc['user_input'] for tc in test_cases],
        'response': [tc['response'] for tc in test_cases],
        'retrieved_contexts': [tc['retrieved_contexts'] for tc in test_cases],
        'reference': [tc['reference'] for tc in test_cases]
    })

    # Evaluate
    results = evaluate(dataset, metrics=metrics)

    return results

# Example test cases
test_cases = [
    {
        'user_input': "How do I check if a cashier can void orders?",
        'response': "Query the SecGrp table: SELECT VoidOrder FROM SecGrp "
                   "WHERE SecGrpName = 'Cashier'. If VoidOrder = 1, they can void.",
        'retrieved_contexts': [
            "The SecGrp table controls permissions.",
            "VoidOrder column indicates void capability.",
            "SELECT * FROM SecGrp WHERE SecGrpName = @Name"
        ],
        'reference': "Check SecGrp.VoidOrder for the Cashier security group. "
                    "Value of 1 means void permission is enabled."
    },
    {
        'user_input': "Why isn't the printer working?",
        'response': "Check the Printer table for configuration. Use "
                   "SELECT * FROM Printer WHERE PrinterID = @ID to see settings.",
        'retrieved_contexts': [
            "Printer table stores printer configuration",
            "PrinterQueue contains active print jobs",
            "Common issues: incorrect IP address, offline status"
        ],
        'reference': "Verify Printer table configuration and check PrinterQueue "
                    "for stuck jobs. Ensure printer is online and IP is correct."
    }
]

# Run evaluation
results = evaluate_escalation_helper(test_cases)

print("\n=== RAGAS Evaluation Results ===")
for metric, score in results.items():
    print(f"{metric}: {score:.3f}")
```

---

## 3. Metric Selection Guide

### Quick Reference Table

| Metric | What It Measures | Best For | Escalation Helper Relevance | Difficulty |
|--------|-----------------|----------|---------------------------|------------|
| **Faithfulness** | Claims supported by context | Preventing hallucinations | HIGH - SQL must be accurate | Medium |
| **Context Recall** | Retrieved all necessary info | Ensuring completeness | HIGH - Need all relevant queries | Medium |
| **Answer Relevancy** | Answer addresses question | User satisfaction | MEDIUM - Important but secondary | Medium |
| **Precision@K** | Quality of top K results | Result quality | MEDIUM - Using reranking | Easy |
| **Recall@K** | Completeness of retrieval | Finding all relevant docs | HIGH - Don't miss SQL fixes | Easy |
| **MRR** | Rank of first relevant | Single-answer queries | HIGH - Often one best query | Easy |
| **NDCG** | Ranking quality | Graded relevance | MEDIUM - If you have relevance scores | Medium |
| **Hit Rate** | Any relevant retrieved? | Baseline check | MEDIUM - Quick health check | Easy |
| **Context Precision** | Context quality | Reducing noise | MEDIUM - Optimizing retrieval | Medium |
| **Factual Correctness** | Factual accuracy | Accuracy validation | HIGH - SQL accuracy critical | Hard |

### Metric Combinations by Use Case

#### Use Case 1: Initial System Validation
**Goal**: Quick check if system is working

**Metrics**:
- Hit Rate@5: Are we finding ANY relevant results?
- Precision@3: Are top results relevant?
- Faithfulness: Are we hallucinating?

**Why**: Fast to compute, covers basics

---

#### Use Case 2: Retrieval Optimization
**Goal**: Improve document retrieval before generation

**Metrics**:
- Recall@K: Are we finding all relevant docs?
- NDCG@K: Is ranking quality good?
- Context Precision: Are we retrieving noise?

**Why**: Focuses on retrieval pipeline specifically

---

#### Use Case 3: Generation Quality
**Goal**: Improve LLM response quality

**Metrics**:
- Faithfulness: Preventing hallucinations
- Answer Relevancy: Staying on topic
- Factual Correctness: Accuracy vs ground truth

**Why**: Focuses on LLM output quality

---

#### Use Case 4: End-to-End RAG Evaluation
**Goal**: Comprehensive system assessment

**Metrics**:
- MRR: Ranking quality
- Context Recall: Retrieval completeness
- Faithfulness: Generation accuracy
- Answer Relevancy: User satisfaction

**Why**: Covers entire pipeline

---

#### Use Case 5: A/B Testing Changes
**Goal**: Compare two system versions

**Metrics**:
- Precision@3 and Recall@5: Retrieval comparison
- Faithfulness: Hallucination rate
- User satisfaction survey (if available)

**Why**: Actionable comparison metrics

---

## 4. Recommended Thresholds

### For Escalation Helper Specifically

Based on the application characteristics:
- Mission-critical SQL queries
- Technical support context
- Expert users (HungerRush install team)

| Metric | Minimum | Target | Excellent | Rationale |
|--------|---------|--------|-----------|-----------|
| **Faithfulness** | 0.85 | 0.90 | 0.95+ | SQL must come from docs, hallucinations are critical failures |
| **Context Recall** | 0.80 | 0.85 | 0.90+ | Must retrieve all relevant troubleshooting steps |
| **Answer Relevancy** | 0.75 | 0.85 | 0.90+ | Answers should address question but context matters |
| **Precision@3** | 0.60 | 0.75 | 0.85+ | At least 2 of 3 results should be relevant |
| **Recall@5** | 0.70 | 0.80 | 0.90+ | Should find most relevant queries in top 5 |
| **MRR** | 0.70 | 0.80 | 0.90+ | Best answer should rank high |
| **Hit Rate@5** | 0.90 | 0.95 | 0.98+ | Almost always find something relevant |
| **NDCG@5** | 0.70 | 0.80 | 0.90+ | Good ranking of results |

### Industry Benchmarks (General RAG Systems)

| Metric | Acceptable | Good | Excellent |
|--------|-----------|------|-----------|
| Faithfulness | 0.70+ | 0.80+ | 0.90+ |
| Context Recall | 0.60+ | 0.75+ | 0.85+ |
| Answer Relevancy | 0.70+ | 0.80+ | 0.90+ |
| Precision@5 | 0.50+ | 0.70+ | 0.85+ |
| MRR | 0.50+ | 0.70+ | 0.85+ |

### When to Adjust Thresholds

**Lower thresholds if**:
- Early development stage
- Very diverse query types
- Limited training data
- Exploratory use case

**Raise thresholds if**:
- Production system
- Safety-critical application (like SQL queries)
- High user expertise
- Well-defined domain

---

## 5. Implementation Examples

### Complete Evaluation Pipeline for Escalation Helper

```python
import json
from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime

# Evaluation framework
@dataclass
class EvaluationResult:
    timestamp: str
    retrieval_metrics: Dict[str, float]
    generation_metrics: Dict[str, float]
    passed_thresholds: bool
    details: Dict

class EscalationHelperEvaluator:
    """Complete evaluation pipeline for Escalation Helper"""

    def __init__(self, llm, embeddings):
        self.llm = llm
        self.embeddings = embeddings

        # Define thresholds
        self.thresholds = {
            'faithfulness': 0.85,
            'context_recall': 0.80,
            'answer_relevancy': 0.75,
            'precision@3': 0.60,
            'recall@5': 0.70,
            'mrr': 0.70,
            'hit_rate@5': 0.90
        }

    def evaluate_retrieval(self, queries_results: List[tuple]) -> Dict[str, float]:
        """
        Evaluate retrieval performance

        Args:
            queries_results: List of (retrieved_docs, relevant_docs) tuples
        """
        metrics = {}

        # Precision@3
        p3_scores = [
            precision_at_k(retrieved, relevant, 3)
            for retrieved, relevant in queries_results
        ]
        metrics['precision@3'] = sum(p3_scores) / len(p3_scores)

        # Recall@5
        r5_scores = [
            recall_at_k(retrieved, relevant, 5)
            for retrieved, relevant in queries_results
        ]
        metrics['recall@5'] = sum(r5_scores) / len(r5_scores)

        # MRR
        metrics['mrr'] = mean_reciprocal_rank(queries_results)

        # Hit Rate@5
        metrics['hit_rate@5'] = hit_rate_at_k(queries_results, 5)

        # F1@5
        f1_scores = [
            f1_at_k(retrieved, relevant, 5)
            for retrieved, relevant in queries_results
        ]
        metrics['f1@5'] = sum(f1_scores) / len(f1_scores)

        return metrics

    def evaluate_generation(self, test_cases: List[Dict]) -> Dict[str, float]:
        """
        Evaluate generation quality using RAGAS

        Args:
            test_cases: List of evaluation samples
        """
        from ragas import evaluate
        from ragas.metrics import (
            Faithfulness,
            AnswerRelevancy,
            ContextRecall
        )
        from datasets import Dataset

        # Create dataset
        dataset = Dataset.from_dict({
            'user_input': [tc['user_input'] for tc in test_cases],
            'response': [tc['response'] for tc in test_cases],
            'retrieved_contexts': [tc['retrieved_contexts'] for tc in test_cases],
            'reference': [tc['reference'] for tc in test_cases]
        })

        # Initialize metrics
        metrics_list = [
            Faithfulness(llm=self.llm),
            AnswerRelevancy(llm=self.llm, embeddings=self.embeddings),
            ContextRecall(llm=self.llm)
        ]

        # Evaluate
        results = evaluate(dataset, metrics=metrics_list)

        return dict(results)

    def evaluate_full_pipeline(
        self,
        retrieval_results: List[tuple],
        generation_test_cases: List[Dict]
    ) -> EvaluationResult:
        """Complete evaluation of retrieval + generation"""

        # Evaluate retrieval
        retrieval_metrics = self.evaluate_retrieval(retrieval_results)

        # Evaluate generation
        generation_metrics = self.evaluate_generation(generation_test_cases)

        # Check thresholds
        all_metrics = {**retrieval_metrics, **generation_metrics}
        passed = all(
            all_metrics.get(metric, 0) >= threshold
            for metric, threshold in self.thresholds.items()
        )

        # Create result
        result = EvaluationResult(
            timestamp=datetime.now().isoformat(),
            retrieval_metrics=retrieval_metrics,
            generation_metrics=generation_metrics,
            passed_thresholds=passed,
            details={
                'thresholds': self.thresholds,
                'failures': [
                    metric for metric, threshold in self.thresholds.items()
                    if all_metrics.get(metric, 0) < threshold
                ]
            }
        )

        return result

    def generate_report(self, result: EvaluationResult) -> str:
        """Generate human-readable evaluation report"""
        report = f"""
        ===== ESCALATION HELPER EVALUATION REPORT =====
        Timestamp: {result.timestamp}
        Overall: {'PASSED' if result.passed_thresholds else 'FAILED'}

        RETRIEVAL METRICS:
        """

        for metric, score in result.retrieval_metrics.items():
            threshold = self.thresholds.get(metric, 'N/A')
            status = '✓' if (threshold == 'N/A' or score >= threshold) else '✗'
            report += f"\n  {status} {metric}: {score:.3f} (threshold: {threshold})"

        report += "\n\n        GENERATION METRICS:\n"

        for metric, score in result.generation_metrics.items():
            threshold = self.thresholds.get(metric, 'N/A')
            status = '✓' if (threshold == 'N/A' or score >= threshold) else '✗'
            report += f"\n  {status} {metric}: {score:.3f} (threshold: {threshold})"

        if result.details['failures']:
            report += "\n\n        FAILED METRICS:\n"
            for metric in result.details['failures']:
                report += f"\n  - {metric}"

        return report

# Usage example
def run_evaluation():
    """Complete evaluation workflow"""
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings

    # Initialize
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embeddings = OpenAIEmbeddings()
    evaluator = EscalationHelperEvaluator(llm, embeddings)

    # Prepare retrieval test data
    retrieval_results = [
        # (retrieved_docs, relevant_docs)
        (['sql_ref_void', 'sql_ref_perms', 'erd_secgrp'], {'sql_ref_void', 'sql_ref_perms'}),
        (['sql_ref_printer', 'sql_ref_queue'], {'sql_ref_printer', 'sql_ref_queue', 'sql_ref_config'}),
        # Add more test queries...
    ]

    # Prepare generation test data
    generation_test_cases = [
        {
            'user_input': "How do I check cashier void permissions?",
            'response': "Query SecGrp: SELECT VoidOrder FROM SecGrp WHERE SecGrpName = 'Cashier'",
            'retrieved_contexts': [
                "SecGrp table controls permissions",
                "VoidOrder column indicates void capability"
            ],
            'reference': "Check SecGrp.VoidOrder for Cashier security group"
        },
        # Add more test cases...
    ]

    # Run evaluation
    result = evaluator.evaluate_full_pipeline(
        retrieval_results,
        generation_test_cases
    )

    # Generate report
    report = evaluator.generate_report(result)
    print(report)

    # Save results
    with open('evaluation_results.json', 'w') as f:
        json.dump({
            'timestamp': result.timestamp,
            'retrieval_metrics': result.retrieval_metrics,
            'generation_metrics': result.generation_metrics,
            'passed': result.passed_thresholds,
            'details': result.details
        }, f, indent=2)

    return result

# Run it
# result = run_evaluation()
```

---

### Continuous Monitoring

```python
import logging
from collections import deque
from datetime import datetime, timedelta

class MetricsMonitor:
    """Monitor metrics over time for degradation detection"""

    def __init__(self, window_size=100):
        self.window_size = window_size
        self.metrics_history = {
            'faithfulness': deque(maxlen=window_size),
            'precision@3': deque(maxlen=window_size),
            'mrr': deque(maxlen=window_size)
        }
        self.timestamps = deque(maxlen=window_size)

    def record_query(self, metrics: Dict[str, float]):
        """Record metrics for a single query"""
        self.timestamps.append(datetime.now())
        for metric, value in metrics.items():
            if metric in self.metrics_history:
                self.metrics_history[metric].append(value)

    def get_moving_average(self, metric: str, window: int = 20) -> float:
        """Calculate moving average for a metric"""
        if metric not in self.metrics_history:
            return 0.0

        recent = list(self.metrics_history[metric])[-window:]
        return sum(recent) / len(recent) if recent else 0.0

    def detect_degradation(self, metric: str, threshold: float, window: int = 20) -> bool:
        """Detect if metric has degraded below threshold"""
        avg = self.get_moving_average(metric, window)
        return avg < threshold

    def alert_if_degraded(self):
        """Check all metrics and log alerts"""
        thresholds = {
            'faithfulness': 0.85,
            'precision@3': 0.60,
            'mrr': 0.70
        }

        for metric, threshold in thresholds.items():
            if self.detect_degradation(metric, threshold):
                logging.warning(
                    f"ALERT: {metric} degraded below {threshold}. "
                    f"Current 20-query average: {self.get_moving_average(metric, 20):.3f}"
                )

# Usage in production
monitor = MetricsMonitor()

def process_user_query(query, system):
    """Process query and monitor metrics"""
    # Get response
    retrieved_docs = system.retrieve(query)
    response = system.generate(query, retrieved_docs)

    # Calculate metrics (simplified)
    metrics = {
        'precision@3': calculate_precision(retrieved_docs),
        'mrr': calculate_mrr(retrieved_docs),
        # Faithfulness would require async evaluation
    }

    # Record for monitoring
    monitor.record_query(metrics)
    monitor.alert_if_degraded()

    return response
```

---

## Summary

### Key Takeaways

1. **Retrieval Metrics** (Easy to compute, run on every query):
   - Precision@K: Result quality
   - Recall@K: Completeness
   - MRR: Ranking of first relevant result
   - Use these for fast iteration and monitoring

2. **Generation Metrics** (LLM-based, slower, use for deep evaluation):
   - Faithfulness: Prevent hallucinations (CRITICAL for Escalation Helper)
   - Context Recall: Ensure completeness
   - Answer Relevancy: User satisfaction
   - Use these for validation and A/B testing

3. **For Escalation Helper**:
   - Prioritize Faithfulness (SQL accuracy is critical)
   - Monitor MRR (users need quick answers)
   - Track Context Recall (don't miss relevant fixes)
   - Set high thresholds (technical users, critical data)

4. **Practical Workflow**:
   - Start with retrieval metrics (fast feedback)
   - Use RAGAS for deeper analysis (slower but comprehensive)
   - Monitor continuously in production
   - A/B test changes with metrics

### Next Steps

1. Implement retrieval metrics for quick iteration
2. Create test set with ground truth annotations
3. Run RAGAS evaluation on test set
4. Set up continuous monitoring
5. Iterate and improve based on metrics

### Additional Resources

- RAGAS Documentation: https://docs.ragas.io/
- Retrieval Metrics: https://en.wikipedia.org/wiki/Evaluation_measures_(information_retrieval)
- RAG Evaluation Best Practices: https://www.anthropic.com/research/evaluating-rag-systems
