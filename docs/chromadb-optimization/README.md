# ChromaDB Optimization Guide

A comprehensive guide to optimizing ChromaDB for the Escalation Helper RAG application.

## What's This About?

This guide covers everything you need to know about making ChromaDB search better for your SQL troubleshooting assistant. Whether you're getting irrelevant results, missing obvious matches, or just want to understand how vector search works under the hood, you're in the right place.

## Quick Links

| Guide | What You'll Learn | Effort | Impact |
|-------|-------------------|--------|--------|
| [01 - How ChromaDB Works](01-how-chromadb-works.md) | Vector search fundamentals, why searches sometimes fail | Read only | Foundation |
| [02 - Quick Wins](02-quick-wins.md) | Distance thresholds, cosine vs L2, filtering bad results | Low | High |
| [03 - HNSW Parameters](03-hnsw-parameters.md) | Index tuning, M/ef parameters, when to change defaults | Low | Low-Medium |
| [04 - Cross-Encoder Reranking](04-cross-encoder-reranking.md) | Two-stage retrieval, significant accuracy boost | Medium | High |
| [05 - Query Expansion](05-query-expansion.md) | GPT-powered query variations, HyDE technique | Medium | Medium |
| [06 - Metadata Filtering](06-metadata-filtering.md) | Category filters, where clauses, UI integration | Medium | Medium |
| [07 - Future Enhancements](07-future-enhancements.md) | Hybrid search, fine-tuning, analytics | High | Varies |
| [08 - Implementation Priority](08-implementation-priority.md) | What to implement first, effort vs impact matrix | Read only | Planning |

## Current Project State

Your Escalation Helper currently uses:
- **ChromaDB** with default settings (L2 distance, no HNSW tuning)
- **OpenAI text-embedding-ada-002** for embeddings
- **2000 character chunks** with 200 character overlap
- **Top 3 results** returned per query
- **No distance filtering** (returns results even if irrelevant)

## Top 3 Recommendations for Immediate Implementation

1. **Switch to Cosine Distance** ([Quick Wins](02-quick-wins.md))
   - 5 minutes to implement
   - Better score interpretation for users
   - Requires re-ingesting documents

2. **Add Distance Threshold Filtering** ([Quick Wins](02-quick-wins.md))
   - 10 minutes to implement
   - Prevents hallucination on irrelevant queries
   - Graceful "no results" handling

3. **Implement Cross-Encoder Reranking** ([Reranking Guide](04-cross-encoder-reranking.md))
   - 30 minutes to implement
   - Significant accuracy improvement
   - Adds ~100-300ms latency

## Sources & References

This guide was researched from official documentation:

- [ChromaDB Configuration Docs](https://docs.trychroma.com/docs/collections/configure)
- [ChromaDB Query Docs](https://docs.trychroma.com/docs/querying-collections/query-and-get)
- [Sentence Transformers Cross-Encoders](https://github.com/UKPLab/sentence-transformers/blob/master/docs/pretrained-models/ce-msmarco.md)
- [Pinecone Relevance Guide](https://docs.pinecone.io/guides/optimize/increase-relevance)
- [LangChain RAG Architecture](https://docs.langchain.com/oss/python/langchain/retrieval)

## Dependencies

To use all features in this guide, add to your `requirements.txt`:

```
sentence-transformers>=2.2.0  # For cross-encoder reranking
```

---

*Last updated: December 2024*
