import unittest
import tempfile
from pathlib import Path

from expense_cli import db


class DBTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        db_path = Path(self.tmpdir.name) / "test.db"
        db.set_db_path(str(db_path))

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_add_get(self):
        eid = db.add_expense("coffee", 3.5, tags=["beverage", "coffee"], note="morning")
        r = db.get_expense(eid)
        self.assertIsNotNone(r)
        self.assertEqual(r["title"], "coffee")
        self.assertAlmostEqual(r["amount"], 3.5)
        self.assertIn("coffee", r["tags"])

    def test_update(self):
        eid = db.add_expense("lunch", 10.0, tags=["food"])
        ok = db.update_expense(eid, amount=12.5, tags=["food", "work"])
        self.assertTrue(ok)
        r = db.get_expense(eid)
        self.assertEqual(r["amount"], 12.5)
        self.assertIn("work", r["tags"])

    def test_delete(self):
        eid = db.add_expense("pen", 1.2)
        ok = db.delete_expense(eid)
        self.assertTrue(ok)
        self.assertIsNone(db.get_expense(eid))

    def test_search(self):
        db.add_expense("movie", 15.0, tags=["entertain"])
        db.add_expense("bus", 2.5, tags=["transport"])
        r = db.list_expenses(tag="entertain")
        self.assertEqual(len(r), 1)
        r2 = db.list_expenses(q="bus")
        self.assertEqual(len(r2), 1)


if __name__ == "__main__":
    unittest.main()
