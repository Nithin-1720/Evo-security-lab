import sqlite3
from pathlib import Path

from fastapi import APIRouter


router = APIRouter(
    prefix="/api/customers",
    tags=["Customers"],
)


ROOT = Path(__file__).resolve().parents[2]

DATABASE = ROOT / "lab-data" / "customers.db"


@router.get("/search")
def search_customer(name: str):

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    # INTENTIONALLY VULNERABLE.
    # Do not copy this pattern into production applications.
    query = (
        "SELECT id, name, email, account_type "
        "FROM customers "
        "WHERE name LIKE '%" + name + "%'"
    )

    results = cursor.execute(query).fetchall()

    connection.close()

    return {
        "query": query,
        "customers": [
            dict(row)
            for row in results
        ],
    }