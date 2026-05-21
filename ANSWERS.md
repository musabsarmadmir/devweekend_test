ANSWERS for Technical Assessment

1) How to run (exact commands):

```bash
# from project root
python -m expense_cli add --title "Coffee" --amount 3.5 --tags coffee,food --note "latte"
python -m expense_cli list --q coffee
python -m expense_cli show 1

# run unit tests
python -m unittest discover -v
```

2) Stack choice:

- Language: Python 3 (stdlib only)
- Storage: SQLite (file in `data/expenses.db`)

Reason: Python is widely available, quick for CLIs, and sqlite is lightweight and persistent without extra services. A worse choice would be a hosted DB or complex web framework for this small CLI: it adds setup overhead without benefit.

3) One real edge case handled (see file & line):

- The app stores tags in a separate `expense_tags` table rather than as a single CSV string. This allows tags to contain commas and avoids brittle string-splitting during search and updates. See `expense_cli/db.py` at the tag insert logic.

4) AI usage:

- I used an AI assistant to generate initial scaffolding for the CLI and SQLite helpers and tests, then reviewed and edited the outputs to ensure correctness and safety. I reworked the tag handling (moved to a separate table) and added input validation for amounts.

5) Honest gap:

- The app lacks advanced input validation, internationalization, and a nicer interactive TUI. With another day I'd add robust validation, nicer printing/formatting, and optional CSV import/export.
