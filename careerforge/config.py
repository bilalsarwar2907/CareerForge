import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "claude-haiku-4-5-20251001")
SONNET_MODEL = "claude-sonnet-5"
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 1024))

# Adzuna
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

# API auth (no default on purpose — must come from .env)
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")


# Paths — built from this file's folder, not the current working directory (bug 11)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
KNOWLEDGE_DIR = DATA_DIR / "knowledge"
DB_PATH = DATA_DIR / "career.db"
LOG_PATH = PROJECT_ROOT / "logs" / "app.log"

# RAG
CHUNK_MAX_SENTENCES = 5
CHUNK_OVERLAP = 1
RETRIEVAL_TOP_K = 4
EMBED_MODEL = "all-MiniLM-L6-v2"

# Cost
PRICE_INPUT_TOKEN = 0.00000025
PRICE_OUTPUT_TOKEN = 0.00000125