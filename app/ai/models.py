import os

from langchain_openai import ChatOpenAI


MODEL_NAME = os.getenv(
    "OPENAI_MODEL",
    "gpt-6-luna",
)


def get_model():

    return ChatOpenAI(
        model=MODEL_NAME,
        temperature=0,
    )