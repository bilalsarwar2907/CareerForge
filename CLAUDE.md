# CareerForge — Claude Context

## What This Project Is
An AI-powered career assistant built on the Anthropic Claude API.
Users upload CVs, match to job descriptions, identify skill gaps, generate cover letters, prepare for interviews, and track applications.
Built checkpoint by checkpoint — nothing discarded, everything extends the previous step.

## Run Commands
# Install dependencies
pip install -r requirements.txt

# Run Streamlit UI
streamlit run app.py

# Run tests
python -m pytest tests/ -v

# Run MCP server
python mcp_server.py

## Architecture Rules
- config.py is the single source of truth — never call os.getenv() directly in any other file
- client.py is the ONLY file that calls the Claude API directly
- All prompts live in prompts.py — never write a prompt inline in another file
- SQLite database at data/career.db — never use JSON files for persistent storage
- All tests in tests/ — mock all external APIs (Claude, Adzuna)

## Current State
All 11 checkpoints complete (Phase 0 + Checkpoints 1–10).
Streamlit UI running. 15 tests passing. MCP server connected to Claude Desktop.

## Known Issues

### ChromaDB — Removed
ChromaDB (both PersistentClient and EphemeralClient) was removed due to Python 3.14 threading incompatibilities.
RAG now uses a simple numpy cosine-similarity vector store (in-memory list of embeddings).
Index resets on every restart — same impact as EphemeralClient had.

## Known Pitfalls
- exit 1 does NOT block hooks — use exit 2 to block
- temperature=0 for structured JSON output, higher for creative output
- JSON parsing: never use raw json.loads() — always go through extract_json() in client.py
- ChromaDB: removed — do not re-add. Use numpy vector store in rag.py instead.
- MCP server: import rag lazily inside function body, not at module level
- rag.py: import client lazily inside answer_with_rag() only — module-level import of client causes hang (Anthropic() init + SentenceTransformer PyTorch threads conflict)

## Recovery Protocol
Before any risky change: git add . && git commit -m "recovery point: before [change]"
To restore one file: git checkout HEAD~1 -- [filename]
Stop after 2 failed attempts — document, apply safest workaround, move forward.

## What's Next — FastAPI Migration (Phase 1 priority)

### Phase 1 — FastAPI Backend
1. Create `api/` directory with `main.py` — FastAPI app, CORS configured
2. Pydantic models for all request/response shapes (CV, job match, RAG, applications)
3. Routes: POST /cv/analyze, POST /match, GET /jobs/search, POST /applications, GET /applications, POST /rag/ask
4. Wire routes to existing business logic — no rewrite, thin HTTP wrappers only
5. JWT auth middleware (python-jose + passlib) — login/register, protected routes
6. Test with pytest + httpx alongside Streamlit

### Phase 2 — Persistent RAG
7. Add save_index() / load_index() to rag.py — numpy .npy + json metadata
8. Load on startup if exists, rebuild if not

### Phase 3 — Docker
9. Dockerfile — Python 3.11 base (fixes Python 3.14 threading issues permanently)
10. docker-compose.yml — FastAPI + volume mount for data/
11. .dockerignore
12. Test locally, then push to Azure Container Registry

### Phase 4 — Azure Deploy
13. Azure Container Registry + Container Apps
14. Environment variables → Azure secrets
15. Persistent storage for data/ volume

### Phase 5 — Frontend
16. Vue 3 + Vite in frontend/
17. Components per tab, axios for API calls
18. Streamlit retired

## Run Commands