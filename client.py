import json
import re
from anthropic import Anthropic
from config import ANTHROPIC_API_KEY, DEFAULT_MODEL

client = Anthropic(api_key=ANTHROPIC_API_KEY)


def extract_json(text: str) -> dict:
    """Extract JSON from Claude's response. Handles markdown fences and extra prose."""
    # Try direct parse first
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Try to extract JSON from markdown fences
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Try to find any JSON object in the text
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Ask Claude to repair the JSON
    return repair_json(text)


def repair_json(broken_text: str) -> dict:
    """Ask Claude to fix broken JSON output."""
    response = client.messages.create(
        model=DEFAULT_MODEL,
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": f"Fix this broken JSON and return only valid JSON, nothing else:\n{broken_text}"
        }]
    )
    repaired = response.content[0].text.strip()
    return json.loads(repaired)


def call_claude(prompt: str, system: str = "", max_tokens: int = 1024,
                temperature: float = 0, stream: bool = False) -> str:
    """Single place for all Claude calls. Returns text."""
    kwargs = dict(
        model=DEFAULT_MODEL,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}]
    )
    if system:
        kwargs["system"] = system

    if stream:
        with client.messages.stream(**kwargs) as s:
            result = ""
            for text in s.text_stream:
                print(text, end="", flush=True)
                result += text
            print()
            return result

    response = client.messages.create(**kwargs)
    return response.content[0].text


def call_claude_json(prompt: str, system: str = "", max_tokens: int = 1024) -> dict:
    """Call Claude and always return a validated dict."""
    text = call_claude(prompt, system=system, max_tokens=max_tokens, temperature=0)
    return extract_json(text)