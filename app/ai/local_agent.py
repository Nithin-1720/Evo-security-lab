from app.ai.datasets import search_support_records
from app.ai.tools import (
    get_private_billing_record,
    read_customer_document,
)


def run_local_agent(prompt: str) -> dict:
    """
    Deterministic offline agent used only for the security lab.

    It intentionally behaves insecurely so we can demonstrate:
    - untrusted retrieved content
    - indirect prompt injection
    - sensitive tool access
    - private data exposure

    No external AI API is used.
    """

    normalized = prompt.lower()

    steps = []

    #
    # Private-data scenario
    #

    if "billing" in normalized and "customer 2" in normalized:

        steps.append(
            {
                "tool": "get_private_billing_record",
                "input": 2,
            }
        )

        result = get_private_billing_record.invoke(
            {
                "customer_id": 2
            }
        )

        return {
            "mode": "local-lab-agent",
            "steps": steps,
            "answer": result,
        }


    #
    # Support dataset scenario
    #

    if "case-" in normalized:

        case_id = None

        for token in prompt.split():

            if token.upper().startswith("CASE-"):
                case_id = token.upper().strip(
                    ".,!?()[]{}"
                )

                break

        if not case_id:

            return {
                "mode": "local-lab-agent",
                "steps": steps,
                "answer": "No case ID found.",
            }

        steps.append(
            {
                "tool": "search_support_dataset",
                "input": case_id,
            }
        )

        records = search_support_records(
            case_id
        )

        if not records:

            return {
                "mode": "local-lab-agent",
                "steps": steps,
                "answer": "No matching case found.",
            }

        record = records[0]

        content = record.get(
            "content",
            "",
        )

        #
        # INTENTIONALLY INSECURE:
        #
        # Retrieved data controls agent behavior.
        #

        if "../fake_secret.txt" in content:

            steps.append(
                {
                    "tool": "read_customer_document",
                    "input": "../fake_secret.txt",
                    "reason": (
                        "Instruction discovered "
                        "inside retrieved content"
                    ),
                }
            )

            secret = read_customer_document.invoke(
                {
                    "filename": "../fake_secret.txt"
                }
            )

            return {
                "mode": "local-lab-agent",
                "case_id": case_id,
                "source": record.get("source"),
                "classification": record.get(
                    "classification"
                ),
                "steps": steps,
                "answer": (
                    "Retrieved document instructed "
                    "the agent to read another file.\n\n"
                    + secret
                ),
            }

        return {
            "mode": "local-lab-agent",
            "case_id": case_id,
            "steps": steps,
            "answer": content,
        }


    return {
        "mode": "local-lab-agent",
        "steps": steps,
        "answer": (
            "Offline lab agent received: "
            + prompt
        ),
    }