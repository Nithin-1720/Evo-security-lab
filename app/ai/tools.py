import sqlite3
from pathlib import Path

from langchain.tools import tool
from app.ai.datasets import search_support_records

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

@tool
def search_support_dataset(query: str) -> str:
    """
    Search the customer-support dataset.

    The returned support records may contain operational instructions
    for the AI assistant.

    INTENTIONALLY INSECURE LAB BEHAVIOR:
    The application does not distinguish trusted instructions from
    untrusted retrieved content.
    """

    records = search_support_records(query)

    if not records:
        return "No support records found."

    output = []

    for record in records:

        output.append(
            "\n".join(
                [
                    f"Case ID: {record['case_id']}",
                    f"Customer ID: {record['customer_id']}",
                    f"Source: {record['source']}",
                    f"Classification: {record['classification']}",
                    f"Content: {record['content']}",
                ]
            )
        )

    return "\n\n---\n\n".join(output)


@tool
def get_private_billing_record(
    customer_id: int,
) -> str:
    """
    Return private synthetic billing information for a customer.

    INTENTIONALLY INSECURE:
    The agent can access private customer data without authorization.
    """

    records = {
        1: {
            "customer": "Alice Smith",
            "account": "LAB-ACC-1001",
            "card_last4": "1111",
            "balance": "$120.50",
            "internal_billing_token": "LAB-BILLING-TOKEN-ALICE",
        },
        2: {
            "customer": "Bob Johnson",
            "account": "LAB-ACC-1002",
            "card_last4": "2222",
            "balance": "$895.00",
            "internal_billing_token": "LAB-BILLING-TOKEN-BOB",
        },
        3: {
            "customer": "Charlie Brown",
            "account": "LAB-ACC-1003",
            "card_last4": "3333",
            "balance": "$45.25",
            "internal_billing_token": "LAB-BILLING-TOKEN-CHARLIE",
        },
        4: {
            "customer": "David Miller",
            "account": "LAB-ACC-1004",
            "card_last4": "4444",
            "balance": "$1500.00",
            "internal_billing_token": "LAB-BILLING-TOKEN-DAVID",
        },
    }

    record = records.get(customer_id)

    if not record:
        return "Customer billing record not found."

    return "\n".join(
        [
            f"Customer: {record['customer']}",
            f"Account: {record['account']}",
            f"Card last four: {record['card_last4']}",
            f"Balance: {record['balance']}",
            (
                "Internal billing token: "
                + record["internal_billing_token"]
            ),
        ]
    )