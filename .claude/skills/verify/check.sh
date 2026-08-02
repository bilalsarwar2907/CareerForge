#!/bin/bash
set -e

echo "=== Gate 1: Running tests ==="
python -m pytest tests/ -v
if [ $? -ne 0 ]; then
  echo "❌ Tests failed"
  exit 2
fi

echo "=== Gate 2: Git diff ==="
git diff

echo "=== Gate 3: Checking for weakened tests ==="
if git diff | grep -E "^\-.*assert|skip|xfail" > /dev/null 2>&1; then
  echo "❌ Weakened test detected — assert removed, test skipped, or xfail added"
  exit 2
fi

echo "✅ PASS — all gates green"