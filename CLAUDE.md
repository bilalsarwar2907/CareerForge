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

## What's Next
1. Fix ChromaDB persistence (pick one option above)
2. Add real CV PDF to data/pdfs/ and test full workflow
3. Expand knowledge base in data/knowledge/
4. Conversation history — multi-turn memory in main.py
5. Frontend upgrade — Vue.js + FastAPI
6. Cloud deploy — Docker image to Azure Container Registry