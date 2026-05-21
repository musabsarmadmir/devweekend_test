Expense CLI — Persistent mini-app

Run the CLI (single command):

```bash
python -m expense_cli add --title "Coffee" --amount 3.5 --tags coffee,food --note "latte"
```

Examples:

```bash
# add an expense (interactive if flags missing)
python -m expense_cli add

# list expenses
python -m expense_cli list --tag coffee

# search text
python -m expense_cli list --q coffee

# show one
python -m expense_cli show 1

# update
python -m expense_cli update 1 --amount 4.0 --tags coffee,personal

# delete
python -m expense_cli delete 1

# run unit tests
python -m unittest discover -v
```

Requirements: Python 3.8+ (uses only stdlib) — no extra packages required.

The SQLite database is stored by default in `data/expenses.db` inside the project directory.

Scaffolded and tested by an automated assistant during the assessment.
