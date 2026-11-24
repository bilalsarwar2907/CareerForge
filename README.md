# CareerForge

A career helper app built with the Claude API (Anthropic).
It reads your CV, compares it with a job, finds jobs, and keeps a list of your applications.

This is a learning project. I build it step by step and keep the code simple.

---

## What it can do

- **CV Analysis** – paste your CV and get a short summary, your skills and tips.
- **Job Match** – paste your CV and a job text and get a score, strengths and gaps.
- **Job Search** – find jobs from Remotive (remote jobs) and Adzuna (UK jobs).
- **Applications** – save the jobs you applied for (stored in SQLite).
- **Career Assistant** – ask career questions. Answers use my own career notes (RAG).

You can use it in three ways:
- **Streamlit** – a simple web page with 5 tabs.
- **REST API** – FastAPI with login (JWT token).
- **Claude Desktop** – through an MCP server.

---

## Tools used

| Part | Tool |
|---|---|
| AI model | Claude (Haiku by default) |
| Search in my notes (RAG) | sentence-transformers + numpy + BM25 |
| Job data | Remotive, Adzuna |
| Database | SQLite |
| Web page | Streamlit |
| API | FastAPI + JWT login |
| Claude Desktop | FastMCP |
| Tests | pytest, 36 tests (Claude calls are faked, so tests cost nothing) |
| Run anywhere | Docker |
| Auto tests on GitHub | GitHub Actions |

---

## Folders

```
careerforge/
├── config.py        settings in one place
├── logger.py        logs each Claude call and its cost
├── llm/             talks to Claude + all prompts
├── agent/           agent that can use tools
├── rag/             search in my career notes
├── tools/           job search + saved applications
├── pdf/             read a CV from a PDF
├── pipeline/        CareerService (match + CV analysis) and a 6-step workflow
├── api/             FastAPI app and login
├── mcp/             MCP server for Claude Desktop
└── ui/              Streamlit app
scripts/evaluate.py  tests different prompts
tests/               pytest tests
```

**CareerService** is one class that does Job Match and CV Analysis.
Streamlit, the API and the workflow all use it, so the logic lives in one place.

---

## How to run it

You need Python 3.11 or 3.12.

```bash
git clone https://github.com/bilalsarwar2907/CareerForge.git
cd CareerForge
python -m venv .venv
.venv\Scripts\Activate.ps1          # Windows (on Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
pip install -e .
```

Copy `.env.example` to `.env` and fill in your keys:

```
ANTHROPIC_API_KEY=your_key_here
DEFAULT_MODEL=claude-haiku-4-5-20251001
ADZUNA_APP_ID=your_app_id
ADZUNA_APP_KEY=your_app_key
JWT_SECRET_KEY=generate_your_own
```

Make a `JWT_SECRET_KEY` with:
`python -c "import secrets; print(secrets.token_urlsafe(32))"`
The API will not start without it.

Start the Streamlit app:
```bash
python -m streamlit run careerforge/ui/app.py
```

Start the API (docs at http://localhost:8888/docs):
```bash
python -m uvicorn careerforge.api.main:app --port 8888
```

Run the tests:
```bash
python -m pytest -q
```

Run with Docker:
```bash
docker compose up --build
```

---

## Some choices I made

- **Settings in one file** – model names and paths come from `config.py`.
- **Safe JSON** – Claude's answer is read with `extract_json()`. If the JSON is broken, it asks Claude once to fix it.
- **Built-in retry** – I use the retry that comes with the Anthropic SDK instead of writing my own.
- **Simple RAG** – no vector database. Embeddings are saved as a numpy file. Search mixes meaning (vectors) and keywords (BM25).
- **Login on the API** – all API routes except register, login and health need a token.
- **Prompt test** – I tested 3 prompt styles on 20 examples and picked the best one.

| Prompt | Valid JSON | All fields | Score correct |
|---|---|---|---|
| V1 Zero-shot | 100% | 100% | **90%** |
| V2 Few-shot | 100% | 100% | 80% |
| V3 XML | 100% | 100% | 85% |

---

## Still to do

- Fix: the API's CV Analysis does not return the summary and tips yet.
- Split `tools.py` into smaller parts.
- Make all Claude calls go through one file (`llm/client.py`).
- Make the match score more strict.
- Pin all package versions.

---

## Author

Bilal Sarwar – [github.com/bilalsarwar2907](https://github.com/bilalsarwar2907)
