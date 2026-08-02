# Verify Skill

## When to trigger
Run this skill after any code change, before marking a task complete.

## Procedure
1. Run the test suite — `python -m pytest tests/ -v`
2. Read the git diff — `git diff` — read what actually changed, not your own summary
3. Check no test was weakened — no `assert` removed, no test skipped, no condition loosened

## Pass condition
All three gates green = ✅ PASS. Done means the skill completed, not that the code looks right.