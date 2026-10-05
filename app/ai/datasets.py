import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_FILE = (
    PROJECT_ROOT
    / "lab-data"
    / "ai-datasets"
    / "support_cases.jsonl"
)


DATASET_NAME = "evo-lab/customer-support-cases"


def load_support_records() -> list[dict]:
    records = []

    if not DATASET_FILE.exists():
        return records

    with DATASET_FILE.open(
        "r",
        encoding="utf-8",
    ) as handle:

        for line in handle:

            line = line.strip()

            if not line:
                continue

            records.append(
                json.loads(line)
            )

    return records


def search_support_records(query: str) -> list[dict]:

    query = query.lower().strip()

    records = load_support_records()

    matches = []

    for record in records:

        searchable = " ".join(
            [
                str(record.get("case_id", "")),
                str(record.get("customer_id", "")),
                str(record.get("source", "")),
                str(record.get("classification", "")),
                str(record.get("content", "")),
            ]
        ).lower()

        if query in searchable:
            matches.append(record)

    return matches


def dataset_metadata() -> dict:

    return {
        "name": DATASET_NAME,
        "type": "local-jsonl",
        "path": str(DATASET_FILE),
        "records": len(load_support_records()),
    }