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

## Known Issues (Unresolved)

### ChromaDB PersistentClient Hang (Checkpoint 4)
**Problem:** `chromadb.PersistentClient` hangs indefinitely when `SentenceTransformer` 
is loaded in the same Python process on this machine (Windows, Python 3.14.3, ChromaDB 0.6.3).
**Workaround:** Using `EphemeralClient` — index resets on every restart.
**Impact:** RAG knowledge base is not persistent between sessions.
**To fix:** Try ChromaDB 0.4.x, or run ChromaDB as a separate server process, 
or replace with FAISS.
**Must resolve before:** Checkpoint 8 (Production Hardening).

## Rules for Debugging and Recovery

### How Claude should behave when something breaks
1. Say "I don't know" upfront if the cause is unclear — never pretend to be certain
2. Diagnose by isolation — test each component alone before combining
3. If 2 attempts fail, stop and explain the options clearly before trying more
4. Never apply a fix that destroys previously working code without a recovery point first

### Recovery points — do this before any risky change
Before modifying a working file, always create a checkpoint commit:
```bash
git add .
git commit -m "recovery point: before changing [filename]"
```
If the change breaks things, recover with:
```bash
git checkout HEAD~1 -- [filename]
```
This restores the previous version of just that file without losing other work.

### When to stop experimenting
If the same error persists after 2 different fixes — stop, document the issue 
in Known Issues, apply the safest workaround, and move forward. 
Do not let one unresolved issue block the entire learning path.