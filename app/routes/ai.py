import os

from fastapi import APIRouter
from fastapi import HTTPException

from app.ai.agent import get_support_agent


router = APIRouter(
    prefix="/api/ai",
    tags=["AI"],
)


@router.get("/chat")
def chat(prompt: str):

    if not os.getenv("OPENAI_API_KEY"):

        raise HTTPException(
            status_code=503,
            detail=(
                "OPENAI_API_KEY is not configured. "
                "The AI components are installed, "
                "but live model execution is disabled."
            ),
        )

    agent = get_support_agent()

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

    last_message = result["messages"][-1]

    return {
        "response": str(last_message.content)
    }