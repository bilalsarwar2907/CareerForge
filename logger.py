import logging
import json
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("career_forge")

# Haiku pricing
PRICE_INPUT = 0.00000025
PRICE_OUTPUT = 0.00000125


def log_api_call(endpoint: str, usage, model: str = "haiku"):
    cost = usage.input_tokens * PRICE_INPUT + usage.output_tokens * PRICE_OUTPUT
    logger.info(json.dumps({
        "event": "api_call",
        "endpoint": endpoint,
        "model": model,
        "input_tokens": usage.input_tokens,
        "output_tokens": usage.output_tokens,
        "cache_read": getattr(usage, "cache_read_input_tokens", 0),
        "cost_usd": round(cost, 6),
        "ts": datetime.now().isoformat()
    }))
    return cost