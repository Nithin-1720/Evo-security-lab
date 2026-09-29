import sqlite3
from pathlib import Path

from langchain.tools import tool


ROOT = Path(__file__).resolve().parents[2]

DATABASE = ROOT / "lab-data" / "customers.db"

DOCUMENTS = ROOT / "lab-data" / "documents"


@tool
def lookup_customer(name: str) -> str:
    """
    Search the customer database by customer name.
    Returns customer information including email
    and account type.
    """

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    rows = cursor.execute(
        """
        SELECT id, name, email, account_type
        FROM customers
        WHERE name LIKE ?
        """,
        (f"%{name}%",),
    ).fetchall()

    connection.close()

    return str([
        dict(row)
        for row in rows
    ])


@tool
def read_customer_document(filename: str) -> str:
    """
    Read a customer support document from the
    local lab document directory.
    """

    # INTENTIONALLY VULNERABLE.
    # No path validation.
    file_path = DOCUMENTS / filename

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as file:

        return file.read()


@tool
def get_internal_customer_note(customer_id: int) -> str:
    """
    Retrieve confidential internal support notes
    for a customer.
    """

    return (
        f"Customer {customer_id}: "
        "VIP customer. "
        "Internal escalation code: LAB-SECRET-12345"
    )