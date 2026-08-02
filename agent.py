import json
from anthropic import Anthropic
from config import ANTHROPIC_API_KEY, SONNET_MODEL
from tools import TOOLS, execute_tool
from prompts import SYSTEM_PROMPT

client = Anthropic(api_key=ANTHROPIC_API_KEY)


def run_agent(user_message: str):
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = client.messages.create(
            model=SONNET_MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    print("Claude:", block.text)
            break

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"[Tool: {block.name}({block.input})]")
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result)
                    })
            messages.append({"role": "user", "content": tool_results})


if __name__ == "__main__":
    run_agent("Find Python backend jobs in Copenhagen and save the best one")