# metamind-vault-rag

A retrieval engine for a directory of markdown. It watches files, indexes them incrementally, and answers hybrid search queries over them.

Vectors live in sqlite-vec, keywords in SQLite FTS5, and the two are fused with reciprocal rank fusion. Embeddings run in-process through fastembed's ONNX models, so there is no server to stand up and no API key to hold. An optional cross-encoder rescore tier is available through the `rerank` extra.

## Install

```bash
uv tool install metamind-vault-rag
```

## Entry points

| Command | Purpose |
|---|---|
| `metamind-vault-rag-watcher` | Watch a directory and index changes |
| `metamind-vault-rag-indexer` | One-shot full reindex |
| `metamind-vault-rag-http` | Loopback HTTP search API |
| `metamind-vault-rag-server` | stdio MCP server |
| `metamind-vault-rag-doctor` | Environment and index diagnostics |

## Configuration

| Variable | Meaning |
|---|---|
| `VAULT_PATH` | Directory to index |
| `VAULT_COLLECTION` | Collection name, which scopes the index files |
| `VAULT_HTTP_PORT` | Port for the loopback search API |
| `VAULT_STATE_DIR` | Where indexes, caches and logs are written. Defaults to `~/.vault-rag` |

Indexes are written to the state directory, named after the collection, and are never placed inside the corpus. Two clients pointed at different collections, or different state directories, coexist on one machine without either knowing about the other.

## Consumers

Installed by any client that wants retrieval without running a service. The engine holds no opinion about who is asking: it names no client in its output, its environment variables are all `VAULT_`-prefixed, and it writes nothing outside the state directory.

## Development

```bash
uv run --extra dev pytest
```

A client can be pointed at a working copy instead of a release with `uv tool install --from /path/to/this/repo metamind-vault-rag`.

## Licence

MIT
