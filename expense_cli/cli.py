import argparse
from typing import List
from . import db


def _parse_tags(tags_str: str) -> List[str]:
    if tags_str is None:
        return []
    return [t.strip() for t in tags_str.split(",") if t.strip()]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="expense_cli", description="Simple expenses CLI with SQLite persistence.")
    sub = parser.add_subparsers(dest="command")

    p_add = sub.add_parser("add")
    p_add.add_argument("--title", "-t", required=False)
    p_add.add_argument("--amount", "-a", required=False)
    p_add.add_argument("--tags", help="Comma-separated tags", default="")
    p_add.add_argument("--note", "-n", default="")

    p_list = sub.add_parser("list")
    p_list.add_argument("--tag", "-g")
    p_list.add_argument("--q", "-q")
    p_list.add_argument("--limit", "-l", type=int)

    p_show = sub.add_parser("show")
    p_show.add_argument("id", type=int)

    p_update = sub.add_parser("update")
    p_update.add_argument("id", type=int)
    p_update.add_argument("--title")
    p_update.add_argument("--amount")
    p_update.add_argument("--tags")
    p_update.add_argument("--note")

    p_delete = sub.add_parser("delete")
    p_delete.add_argument("id", type=int)

    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "add":
        title = args.title or input("Title: ")
        amount_str = args.amount or input("Amount: ")
        try:
            # accept numbers with commas like 1,234.56
            amount = float(amount_str.replace(",", ""))
        except Exception:
            print("Invalid amount; please enter a number like 12.34")
            return 2
        tags = _parse_tags(args.tags)
        note = args.note
        eid = db.add_expense(title, amount, tags=tags, note=note)
        print(f"Added expense #{eid}")
        return 0

    if args.command == "list":
        results = db.list_expenses(q=args.q, tag=args.tag, limit=args.limit)
        if not results:
            print("No expenses found.")
            return 0
        for r in results:
            tags = ", ".join(r.get("tags") or [])
            print(f"#{r['id']} {r['title']} — ${r['amount']} — tags: {tags} — note: {r.get('note')}")
        return 0

    if args.command == "show":
        r = db.get_expense(args.id)
        if not r:
            print("Not found")
            return 1
        print(f"#{r['id']} {r['title']}")
        print(f"Amount: {r['amount']}")
        print(f"Tags: {', '.join(r['tags'])}")
        print(f"Note: {r.get('note')}")
        print(f"Created: {r.get('created_at')}")
        print(f"Updated: {r.get('updated_at')}")
        return 0

    if args.command == "update":
        tags = _parse_tags(args.tags) if args.tags is not None else None
        amount = None
        if args.amount is not None:
            try:
                amount = float(args.amount.replace(",", ""))
            except Exception:
                print("Invalid amount")
                return 2
        ok = db.update_expense(args.id, title=args.title, amount=amount, tags=tags, note=args.note)
        print("Updated" if ok else "No changes or not found")
        return 0

    if args.command == "delete":
        ok = db.delete_expense(args.id)
        print("Deleted" if ok else "Not found")
        return 0

    return 0
