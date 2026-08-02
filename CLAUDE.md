# CareerForge — Claude Context

## What This Project Is
An AI-powered career assistant built on the Anthropic Claude API.
Users upload CVs, match to job descriptions, identify skill gaps, generate cover letters, prepare for interviews, and track applications.
Built checkpoint by checkpoint — nothing discarded, everything extends the previous step.

## Run Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py

# Run tests
python -m pytest tests/ -v

# Run Streamlit UI (Checkpoint 10)
streamlit run app.py
```

## Architecture Rules
- `config.py` is the single source of truth — never call `os.getenv()` directly in any other file
- `client.py` is the ONLY file that calls the Claude API directly
- All prompts live in `prompts.py` — never write a prompt inline in another file
- SQLite database at `data/career.db` — never use JSON files for persistent storage
- All tests in `tests/` — mock all external APIs (Claude, Adzuna)

## Known Pitfalls
- `exit 1` does NOT block hooks — use `exit 2` to block
- `temperature=0` for structured JSON output, higher for creative output
- JSON parsing: never use raw `json.loads()` — always go through `extract_json()` in client.py

## Current State
Checkpoint 0 complete — scaffold only. No feature code yet.
## Current State
Checkpoint 2 complete — prompt evaluation done, V1 wins at 90% accuracy.



## What's Next
Checkpoint 1 — Claude API fundamentals: config.py, client.py, prompts.py, main.py

## What's Next
Checkpoint 3 — Tool calling: tools.py, agent.py, real Adzuna API, SQLite