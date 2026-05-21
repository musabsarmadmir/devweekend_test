ANSWERS for Technical Assessment

1) How to run (exact commands):

```bash
python3 -m expense_cli add --title "Coffee" --amount 3.5 --tags coffee,food --note "latte"
python3 -m expense_cli list --q coffee
python3 -m expense_cli show 1

# run unit tests
python3 -m unittest discover -v
```

2) Stack choice:

- Language: Python 3
- Storage: SQLite (file in `data/expenses.db`)

Reason: Python is widely available, quick for CLIs, and SQLite is lightweight and persistent without extra services.

Feature beyond CRUD: tagging + search (via `list --tag ...` and `list --q ...`). For real expense tracking, being able to slice by tag (e.g., `food`, `transport`) and quickly find items by keyword is what makes the tool useful.

A worse choice would be a hosted DB or a full web framework for this: it adds setup, deployment, and auth complexity without improving the core user task.

3) One real edge case handled (see file & line):

- The CLI accepts amounts that include thousands separators (e.g. `1,234.56`) and rejects invalid input with a friendly message instead of crashing.
	- Location: `expense_cli/cli.py` lines 47–53 and 86–91.
	- Without this handling, `float("1,234.56")` would raise a `ValueError`, and the CLI would exit with a stack trace.

4) AI usage:

- GitHub Copilot Chat (VS Code)
	- Asked: why the unit tests wouldn’t run / why discovery found 0 tests.
	- Output: explanation of Python import/discovery behavior and options to fix (run from repo root, set `PYTHONPATH`, or make `tests/` importable).
	- Change I made: I avoided recommending `pip install -e .` as the “main” path because on Debian/Ubuntu it can fail under PEP 668 (externally-managed env). Instead, the repo runs with `python3 -m expense_cli ...` and tests run with `python3 -m unittest discover -v`.

5) Honest gap:

- The output formatting is functional but not great (no aligned columns, no currency formatting, no totals). With another day: add better formatting + summaries (totals by tag / time) and more robust validation (negative amounts, empty titles, etc.).
