import sqlite3
from pathlib import Path
from datetime import datetime

from app.auth.passwords import hash_password


DB_PATH = Path("lab-data/customers.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()


# Existing customers table is preserved.
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT
    )
    """
)


cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        display_name TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',

        totp_secret TEXT,
        totp_enabled INTEGER NOT NULL DEFAULT 0,

        otp_enabled INTEGER NOT NULL DEFAULT 0,

        created_at TEXT NOT NULL
    )
    """
)


cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS lab_mailbox (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        recipient TEXT,
        subject TEXT,
        body TEXT,
        otp_code TEXT,
        created_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """
)


cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS audit_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        event_type TEXT,
        details TEXT,
        created_at TEXT
    )
    """
)

# Enable email-style OTP for the analyst demo account.
cursor.execute(
    """
    UPDATE users
    SET otp_enabled = 1
    WHERE username = 'analyst'
    """
)


users = [
    (
        "admin",
        "Lab Administrator",
        hash_password("LabAdmin123!"),
        "admin",
        datetime.utcnow().isoformat(),
    ),
    (
        "analyst",
        "Security Analyst",
        hash_password("LabAnalyst123!"),
        "analyst",
        datetime.utcnow().isoformat(),
    ),
    (
        "user",
        "Demo Customer",
        hash_password("LabUser123!"),
        "user",
        datetime.utcnow().isoformat(),
    ),
]


cursor.executemany(
    """
    INSERT OR IGNORE INTO users
        (username, display_name, password_hash, role, created_at)
    VALUES (?, ?, ?, ?, ?)
    """,
    users,
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS customer_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        note TEXT NOT NULL,
        sensitivity TEXT NOT NULL DEFAULT 'internal',
        FOREIGN KEY(customer_id) REFERENCES customers(id)
    )
    """
)


cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS user_profiles (
        user_id INTEGER PRIMARY KEY,
        email TEXT,
        department TEXT,
        phone TEXT,
        role TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """
)


cursor.execute(
    """
    INSERT OR IGNORE INTO customer_notes
        (id, customer_id, note, sensitivity)
    VALUES
        (1, 1, 'Alice requested an enterprise contract review.', 'internal'),
        (2, 2, 'Bob has an outstanding billing dispute.', 'confidential'),
        (3, 3, 'Charlie is evaluating competitor products.', 'internal'),
        (4, 4, 'David requested privileged support access.', 'confidential')
    """
)


cursor.execute(
    """
    INSERT OR IGNORE INTO user_profiles
        (user_id, email, department, phone, role)
    VALUES
        (1, 'admin@lab.local', 'IT', '555-0101', 'admin'),
        (2, 'analyst@lab.local', 'Security', '555-0102', 'analyst'),
        (3, 'user@lab.local', 'Customer', '555-0103', 'user')
    """
)

connection.commit()


print("Evo Vulnerable AI Lab database initialized.")
print()
print("LAB-ONLY ACCOUNTS")
print("-----------------")
print("admin   / LabAdmin123!")
print("analyst / LabAnalyst123!")
print("user    / LabUser123!")
print()
print("These credentials are intentionally non-production demo credentials.")


connection.close()