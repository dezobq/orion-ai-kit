# RAG Query Patterns for OpenSearch

This document demonstrates BM25 and hybrid search patterns for the `code-chunks` index.

## Prerequisites

- OpenSearch running on `https://localhost:9200` (or `https://opensearch:9200` from Docker)
- Index `code-chunks` created with mapping
- Code ingested via `scripts/ingest_to_opensearch.py`

## BM25 Full-Text Search

### Simple Match Query

Search for code containing specific terms:

```bash
curl -k -u admin:MyS3curePassw0rd!2025 \
  "https://localhost:9200/code-chunks/_search?pretty" \
  -H "Content-Type: application/json" -d '{
    "query": { "match": { "content": "module.exports" } },
    "size": 3,
    "_source": ["path", "start_line", "end_line", "lang"]
  }'
```

**Results:** Files containing "module.exports" (sum.js, jest.config.js, eslint.config.js)

### Match with Highlights

Get matching snippets with highlighted terms:

```bash
curl -k -u admin:MyS3curePassw0rd!2025 \
  "https://localhost:9200/code-chunks/_search?pretty" \
  -H "Content-Type: application/json" -d '{
    "query": { "match": { "content": "jest" } },
    "size": 3,
    "_source": ["path", "start_line", "end_line", "lang", "content"],
    "highlight": { "fields": { "content": {} } }
  }'
```

**Results:** Highlights `<em>jest</em>` in matching content

### Boolean Compound Query

Combine multiple conditions:

```bash
curl -k -u admin:MyS3curePassw0rd!2025 \
  "https://localhost:9200/code-chunks/_search?pretty" \
  -H "Content-Type: application/json" -d '{
    "query": {
      "bool": {
        "should": [
          { "match": { "content": "test expect" } },
          { "match": { "path": "*.test.*" } }
        ]
      }
    },
    "size": 3,
    "_source": ["path", "start_line", "end_line", "lang"]
  }'
```

**Results:** Prioritizes test files and content with "test expect"

### Filter by Language

Search only TypeScript files:

```bash
curl -k -u admin:MyS3curePassw0rd!2025 \
  "https://localhost:9200/code-chunks/_search?pretty" \
  -H "Content-Type: application/json" -d '{
    "query": {
      "bool": {
        "must": { "match": { "content": "function" } },
        "filter": { "term": { "lang": "typescript" } }
      }
    },
    "size": 5,
    "_source": ["path", "start_line", "end_line", "symbol"]
  }'
```

### Search by Path Pattern

Find specific files or directories:

```bash
curl -k -u admin:MyS3curePassw0rd!2025 \
  "https://localhost:9200/code-chunks/_search?pretty" \
  -H "Content-Type: application/json" -d '{
    "query": {
      "bool": {
        "must": { "match": { "content": "config" } },
        "filter": { "wildcard": { "path": "*.config.js" } }
      }
    },
    "size": 5
  }'
```

## Hybrid Search (BM25 + Vector)

**Note:** Requires embeddings to be generated during ingestion (`WITH_EMBEDDINGS=1`)

### Generate Query Embedding

First, generate embedding for your query using the same model (all-MiniLM-L6-v2):

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
query_vector = model.encode("http client retry backoff logic").tolist()
print(query_vector)  # 384-dim vector
```

### Hybrid Query Pattern

Combine BM25 text matching with semantic vector search:

```bash
curl -k -u admin:MyS3curePassw0rd!2025 \
  "https://localhost:9200/code-chunks/_search?pretty" \
  -H "Content-Type: application/json" -d '{
    "size": 5,
    "query": {
      "bool": {
        "should": [
          {
            "match": {
              "content": "http client retry backoff"
            }
          },
          {
            "script_score": {
              "query": { "match_all": {} },
              "script": {
                "source": "cosineSimilarity(params.query_vector, '\''embedding'\'') + 1.0",
                "params": {
                  "query_vector": [0.1, 0.2, ...]  // Replace with actual 384-dim vector
                }
              }
            }
          }
        ]
      }
    },
    "_source": ["path", "start_line", "end_line", "lang", "symbol"]
  }'
```

### KNN-Only Search

Pure vector similarity search (faster than script_score):

```bash
curl -k -u admin:MyS3curePassw0rd!2025 \
  "https://localhost:9200/code-chunks/_search?pretty" \
  -H "Content-Type: application/json" -d '{
    "size": 10,
    "query": {
      "knn": {
        "embedding": {
          "vector": [0.1, 0.2, ...],  // 384-dim query vector
          "k": 50
        }
      }
    },
    "_source": ["path", "start_line", "end_line", "content"]
  }'
```

## Advanced Patterns

### Multi-Match Across Fields

Search in content and path simultaneously:

```bash
curl -k -u admin:MyS3curePassw0rd!2025 \
  "https://localhost:9200/code-chunks/_search?pretty" \
  -H "Content-Type: application/json" -d '{
    "query": {
      "multi_match": {
        "query": "test configuration",
        "fields": ["content^2", "path", "symbol"]
      }
    },
    "size": 5
  }'
```

### Aggregations by Language

Get document counts per language:

```bash
curl -k -u admin:MyS3curePassw0rd!2025 \
  "https://localhost:9200/code-chunks/_search?pretty" \
  -H "Content-Type: application/json" -d '{
    "size": 0,
    "aggs": {
      "languages": {
        "terms": { "field": "lang", "size": 10 }
      }
    }
  }'
```

### Fuzzy Search

Handle typos and variations:

```bash
curl -k -u admin:MyS3curePassw0rd!2025 \
  "https://localhost:9200/code-chunks/_search?pretty" \
  -H "Content-Type: application/json" -d '{
    "query": {
      "match": {
        "content": {
          "query": "confguration",
          "fuzziness": "AUTO"
        }
      }
    },
    "size": 3
  }'
```

## Reranking Pattern

After initial retrieval, rerank with cross-encoder for better precision:

1. **Retrieve candidates** (BM25 or hybrid, top 50-100)
2. **Score with cross-encoder** (CPU-intensive, applied to fewer docs)
3. **Return top K** (final ranked results)

```python
from sentence_transformers import CrossEncoder

# Step 1: Initial retrieval (50 candidates)
candidates = opensearch_search(query, size=50)

# Step 2: Rerank with cross-encoder
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
pairs = [(query, doc['content']) for doc in candidates]
scores = reranker.predict(pairs)

# Step 3: Sort by reranker scores
ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
top_results = [doc for doc, score in ranked[:5]]
```

## Integration with Agentic Workflow

**Planner → Retrieve → Rerank → Implementer → Critic**

1. **Planner**: Generates search query from task description
2. **Retrieve**: Executes hybrid search (BM25 + vector) → top 50 chunks
3. **Rerank**: Cross-encoder scores relevance → top 5-10 chunks
4. **Implementer**: Uses retrieved context to generate code
5. **Critic**: Validates implementation against requirements

## Performance Tips

- Use `size: 0` for aggregations-only queries (faster)
- Filter before scoring when possible (`filter` clause vs `must`)
- Batch queries using `_msearch` API
- Cache frequent queries with `request_cache: true`
- Use `_source: false` if you only need metadata
- For large datasets, use `search_after` instead of `from/size` pagination

## Monitoring

Check index stats:

```bash
curl -k -u admin:MyS3curePassw0rd!2025 \
  "https://localhost:9200/code-chunks/_stats?pretty"
```

View slow queries:

```bash
curl -k -u admin:MyS3curePassw0rd!2025 \
  "https://localhost:9200/_nodes/stats/indices/search?pretty"
```
