import os

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
)

from app.ai.datasets import (
    dataset_metadata,
    search_support_records,
)

from app.ai.evo_agent import build_evo_agent
from app.ai.models import MODEL_NAME
from app.ai.local_agent import run_local_agent

router = APIRouter(
    prefix="/api/ai",
    tags=["AI Security Lab"],
)


@router.get("/assets")
def ai_assets():

    return {
        "model": MODEL_NAME,
        "framework": "LangChain",
        "provider": "OpenAI",
        "agent": "evo_customer_support_agent",
        "dataset": dataset_metadata(),
        "tools": [
            "lookup_customer",
            "search_support_dataset",
            "read_customer_document",
            "get_internal_customer_note",
            "get_private_billing_record",
        ],
        "mcp_server": "Evo Vulnerable Lab MCP",
    }


@router.get("/dataset/search")
def dataset_search(
    query: str = Query(
        ...,
        min_length=1,
    ),
):

    return {
        "query": query,
        "results": search_support_records(query),
    }


@router.get("/chat")
def chat(
    prompt: str = Query(
        ...,
        min_length=1,
    ),
):

    if not os.getenv("OPENAI_API_KEY"):

        raise HTTPException(
            status_code=503,
            detail=(
                "OPENAI_API_KEY is not configured. "
                "Live AI execution is disabled."
            ),
        )

    try:

        agent = build_evo_agent()

        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ]
            }
        )

        messages = result.get(
            "messages",
            [],
        )

        if messages:
            answer = messages[-1].content
        else:
            answer = str(result)

        return {
            "model": MODEL_NAME,
            "prompt": prompt,
            "answer": answer,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                f"AI lab execution failed: "
                f"{type(exc).__name__}: {exc}"
            ),
        )

@router.get("/chat/local")
def local_chat(
    prompt: str = Query(
        ...,
        min_length=1,
    ),
):

    return run_local_agent(prompt)