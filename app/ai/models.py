from langchain_openai import ChatOpenAI


MODEL_NAME = "gpt-5.6-luna"


def get_model():

    model = ChatOpenAI(
        model=MODEL_NAME,
        temperature=0,
    )

    return model