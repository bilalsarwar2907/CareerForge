# CareerForge

An AI-powered career assistant built on the Anthropic Claude API. Upload CVs, match to job descriptions, identify skill gaps, generate cover letters, prepare for interviews, and track applications — all from a browser interface.

Built checkpoint by checkpoint as a structured learning project. Every feature is demonstrable from the code.

---

## What It Does

- **CV Analysis** — paste CV text, get structured summary, skills, and recommendations
- **Job Matching** — score a CV against a job description with strengths and gaps
- **Job Search** — real listings via Adzuna API and Remotive (Denmark/remote focus)
- **Application Tracker** — SQLite-backed application history
- **Career Assistant** — RAG chat answering career questions from your knowledge base
- **REST API** — FastAPI backend with JWT auth, all features exposed as HTTP endpoints

---

## Technical Stack

| Layer | Technology |
|---|---|
| LLM | Anthropic Claude API (Haiku + Sonnet) |
| Vector Search | numpy cosine similarity + sentence-transformers |
| Lexical Search | BM25 (rank-bm25) |
| RAG Persistence | numpy .npy + JSON metadata |
| Job Search API | Adzuna, Remotive |
| Database | SQLite |
| REST API | FastAPI + Pydantic + JWT (python-jose + passlib) |
| MCP Server | FastMCP |
| UI | Streamlit |
| Testing | pytest + FastAPI TestClient (23 tests, all APIs mocked) |
| Deployment | Docker (python:3.11-slim) |

---

## Architecture

```
CareerForge/
├── config.py          — single source of truth for all settings
├── client.py          — only file that calls the Claude API directly
├── prompts.py         — all prompts, versioned and evaluated
├── tools.py           — tool definitions + Adzuna/Remotive API + SQLite
├── agent.py           — tool-calling agent loop
├── rag.py             — sentence chunking, numpy vector store, BM25, hybrid search
├── pdf_handler.py     — PDF extraction + prompt caching
├── workflow.py        — 6-step deterministic pipeline
├── mcp_server.py      — FastMCP server for Claude Desktop
├── logger.py          — API call logging with cost tracking
├── evaluate.py        — prompt evaluation with CSV output
├── app.py             — Streamlit UI
├── api/
│   ├── main.py        — FastAPI app + CORS middleware
│   ├── models.py      — Pydantic request/response models
│   ├── routes.py      — REST routes wired to business logic
│   ├── auth.py        — JWT auth, bcrypt, HTTPBearer
│   └── auth_routes.py — /auth/register + /auth/login
└── tests/
    ├── test_*.py      — 15 unit tests (mocked APIs)
    └── test_api.py    — 8 FastAPI integration tests
```

---

## Key Engineering Decisions

**Hybrid Search** — RAG uses both vector search (numpy cosine similarity) and BM25 lexical search combined. Vector search finds semantically similar content; BM25 finds exact keyword matches. Together they outperform either alone.

**Persistent RAG Index** — embeddings saved to `data/rag_index/embeddings.npy` and metadata to `data/rag_index/metadata.json`. Loaded on startup if present, rebuilt if not. No data loss on restart.

**No ChromaDB** — ChromaDB was removed due to Python 3.14 threading incompatibilities with PyTorch. Replaced with a simple in-memory numpy vector store with disk persistence. Same retrieval quality, zero dependency conflicts.

**Prompt Evaluation** — three prompt versions (zero-shot, few-shot, XML-structured) were tested against 20 labelled test cases. Winner selected by accuracy score, not opinion. Results saved to CSV as evidence.

**JSON Reliability** — `extract_json()` in `client.py` tries four strategies: direct parse, markdown fence extraction, regex search, and Claude self-repair. Raw `json.loads()` is never used directly.

**Single API Surface** — `client.py` is the only file that calls the Anthropic API. All other files import from it. Model names and settings come from `config.py`. Nothing is hardcoded.

**JWT Auth** — FastAPI backend uses HTTPBearer scheme with python-jose JWT tokens and bcrypt-hashed passwords stored in SQLite. All business routes are protected.

**MCP Integration** — CareerForge tools are exposed via FastMCP, allowing Claude Desktop to call `search_jobs`, `save_application`, `get_resume`, `list_applications`, and `ask_career_advisor` directly.

---

## Setup

```bash
git clone https://github.com/bilalsarwar2907/CareerForge.git
cd CareerForge
pip install -r requirements.txt
```

Create `.env`:
```
ANTHROPIC_API_KEY=your_key_here
DEFAULT_MODEL=claude-haiku-4-5-20251001
ADZUNA_APP_ID=your_app_id
ADZUNA_APP_KEY=your_app_key
```

Run the FastAPI backend:
```bash
python -m uvicorn api.main:app --reload --port 8888
```

Run the Streamlit UI:
```bash
python -m streamlit run app.py
```

Run tests:
```bash
python -m pytest tests/ -v
```

Run with Docker:
```bash
docker compose up --build
```

API docs available at: http://localhost:8888/docs

---

## Prompt Evaluation Results

| Prompt | Valid JSON | Fields | Score Accuracy |
|---|---|---|---|
| V1 Zero-shot | 100% | 100% | 90% |
| V2 Few-shot | 100% | 100% | 80% |
| V3 XML | 100% | 100% | 85% |

Winner: V1 Zero-shot at 90% accuracy on 20 test cases.

---

## Portfolio Statement

Built an end-to-end AI career assistant using the Anthropic Claude API. It processes CVs via PDF extraction, scores job matches using prompt-engineered structured outputs with automated evaluation, retrieves career guidance via hybrid vector + BM25 RAG with persistent numpy index, calls real job APIs (Adzuna, Remotive) via tool use, runs a 6-step workflow pipeline, exposes a FastAPI REST backend with JWT authentication, exposes tools via MCP for Claude Desktop integration, and is production-hardened with centralised config, logging, cost tracking, retry logic, mocked pytest coverage, and Docker deployment.

---

## Author

Bilal Sarwar — [github.com/bilalsarwar2907](https://github.com/bilalsarwar2907)
