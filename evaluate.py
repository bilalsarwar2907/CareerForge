import json
import csv
from datetime import datetime
from client import call_claude_json
from prompts import MATCH_PROMPT_V1, MATCH_PROMPT_V2, MATCH_PROMPT_V3

PROMPTS = {
    "v1_zeroshot": MATCH_PROMPT_V1,
    "v2_fewshot": MATCH_PROMPT_V2,
    "v3_xml": MATCH_PROMPT_V3,
}


def evaluate_prompt(prompt_template: str, tests: list) -> dict:
    results = []
    for test in tests:
        prompt = prompt_template.format(cv_text=test["cv"], job_text=test["job"])
        try:
            result = call_claude_json(prompt)
            valid = True
            has_fields = all(k in result for k in ["score", "strengths", "gaps"])
            score = result.get("score", -1)
            in_range = test["expected_score_min"] <= score <= test["expected_score_max"]
        except Exception as e:
            valid = False
            has_fields = False
            in_range = False

        results.append({
            "id": test["id"],
            "valid_json": valid,
            "has_fields": has_fields,
            "score_in_range": in_range,
        })

    total = len(results)
    return {
        "valid_json_pct": sum(r["valid_json"] for r in results) / total * 100,
        "has_fields_pct": sum(r["has_fields"] for r in results) / total * 100,
        "score_accuracy_pct": sum(r["score_in_range"] for r in results) / total * 100,
    }


def run_all():
    with open("data/tests.json") as f:
        tests = json.load(f)

    summary = []
    for name, prompt in PROMPTS.items():
        print(f"Evaluating {name}...")
        metrics = evaluate_prompt(prompt, tests)
        metrics["prompt"] = name
        summary.append(metrics)
        print(f"  Valid JSON: {metrics['valid_json_pct']:.0f}%  "
              f"Fields: {metrics['has_fields_pct']:.0f}%  "
              f"Accuracy: {metrics['score_accuracy_pct']:.0f}%")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"data/eval_{timestamp}.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=summary[0].keys())
        writer.writeheader()
        writer.writerows(summary)

    winner = max(summary, key=lambda x: x["score_accuracy_pct"])
    print(f"\nWinner: {winner['prompt']} ({winner['score_accuracy_pct']:.0f}% accuracy)")


if __name__ == "__main__":
    run_all()