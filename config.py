import os
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

# JSearch (OpenWeb Ninja) — for Denmark job search
JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY")

# Paths
DATA_DIR = "data"
KNOWLEDGE_DIR = f"{DATA_DIR}/knowledge"
CHROMA_DIR = f"{DATA_DIR}/chroma"
DB_PATH = f"{DATA_DIR}/career.db"
LOG_PATH = "logs/app.log"

# RAG
CHUNK_MAX_SENTENCES = 5
CHUNK_OVERLAP = 1
RETRIEVAL_TOP_K = 4
EMBED_MODEL = "all-MiniLM-L6-v2"

# Cost
PRICE_INPUT_TOKEN = 0.00000025
PRICE_OUTPUT_TOKEN = 0.00000125