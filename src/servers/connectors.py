import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from typing_extensions import Coroutine
from langchain_core.messages import AIMessage


class OpenrouterConnector:
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.getenv("openrouter_api_key")
        self.model = model or os.getenv("openrouter_model_name")

    def create_obj(self) -> ChatOpenAI:
        return ChatOpenAI(base_url="https://openrouter.ai/api/v1", api_key=self.api_key, model=self.model)

    def call(self, obj: ChatOpenAI, prompt: str) -> AIMessage:
        return obj.invoke(prompt)

    def acall(self, obj: ChatOpenAI, prompt: str) -> Coroutine:
        return obj.ainvoke(prompt)


class OllamaConnector:
    def __init__(self, model: str | None = None) -> None:
        self.model = model or os.getenv("ollama_model_name")

    def create_obj(self) -> ChatOllama:
        return ChatOllama(model=self.model)

    def call(self, obj: ChatOllama, prompt: str) -> AIMessage:
        return obj.invoke(prompt)

    def acall(self, obj: ChatOpenAI, prompt: str) -> Coroutine:
        return obj.ainvoke(prompt)


#! Usage
# if __name__ == "__main__":
    # import asyncio
    # openrouter_connector = OpenrouterConnector()
    # print(type(asyncio.run(openrouter_connector.acall(
    #     openrouter_connector.create_obj(), "Hi")))
    # )
