import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DATABASE = ROOT / "lab-data" / "customers.db"


DATABASE.parent.mkdir(parents=True, exist_ok=True)


connection = sqlite3.connect(DATABASE)

cursor = connection.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    account_type TEXT NOT NULL
)
""")


cursor.execute("DELETE FROM customers")


customers = [
    ("Alice Smith", "alice@example.test", "standard"),
    ("Bob Johnson", "bob@example.test", "premium"),
    ("Charlie Brown", "charlie@example.test", "admin"),
    ("David Miller", "david@example.test", "standard"),
]


cursor.executemany(
    """
    INSERT INTO customers (name, email, account_type)
    VALUES (?, ?, ?)
    """,
    customers,
)


connection.commit()

connection.close()


print(f"Database created: {DATABASE}")