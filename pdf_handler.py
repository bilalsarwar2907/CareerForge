import base64
from config import SONNET_MODEL
from client import client, extract_json


def analyze_cv_pdf(filepath: str) -> dict:
    """Send a PDF CV directly to Claude and extract structured data."""
    with open(filepath, "rb") as f:
        pdf_data = base64.standard_b64encode(f.read()).decode("utf-8")

    response = client.messages.create(
        model=SONNET_MODEL,
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_data
                    }
                },
                {
                    "type": "text",
                    "text": """Extract from this CV and return JSON only:
{
  "name": "full name",
  "skills": ["skill1", "skill2"],
  "experience_years": integer,
  "education": ["degree1"],
  "languages": ["lang1"]
}"""
                }
            ]
        }]
    )
    return extract_json(response.content[0].text)


def measure_prompt_caching(system_prompt: str, user_message: str) -> list:
    """Run same request twice. Compare cached vs uncached token usage."""
    results = []
    for run in range(2):
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            system=[{
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"}
            }],
            messages=[{"role": "user", "content": user_message}],
            extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"}
        )
        usage = response.usage
        results.append({
            "run": run + 1,
            "input_tokens": usage.input_tokens,
            "output_tokens": usage.output_tokens,
            "cache_read_tokens": usage.cache_read_input_tokens,
            "cache_write_tokens": usage.cache_creation_input_tokens,
        })
        print(f"Run {run+1}: input={usage.input_tokens}, "
              f"cache_read={usage.cache_read_input_tokens}, "
              f"cache_write={usage.cache_creation_input_tokens}")

    return results


if __name__ == "__main__":
    print("=== Testing Prompt Caching ===")
    long_system = """You are a professional career advisor with 20 years of experience.
    """ + ("You help candidates optimize their CVs and prepare for interviews. " * 500)

    results = measure_prompt_caching(long_system, "What is the most important thing on a CV?")
    print(f"\nRun 1 cache_write: {results[0]['cache_write_tokens']} tokens")
    print(f"Run 2 cache_read: {results[1]['cache_read_tokens']} tokens")
    if results[1]['cache_read_tokens'] > 0:
        print("✅ Caching working — Run 2 read from cache")
    else:
        print("⚠️ Cache not activated — prompt may be too short")