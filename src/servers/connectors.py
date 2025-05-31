from langchain_community.chat_models import ChatOllama
from typing import Any, Coroutine, Protocol
from abc import ABC, abstractmethod
import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from typing_extensions import Coroutine
from langchain_core.messages import AIMessage
from typing_extensions import TypedDict
from typing import Literal

load_dotenv()


class BaseConnector(ABC):
    @abstractmethod
    def create_obj(self, structure: Any = None) -> Any:
        pass

    @abstractmethod
    def call(self, obj: Any, prompt: str) -> AIMessage:
        pass

    @abstractmethod
    def acall(self, obj: Any, prompt: str) -> Coroutine:
        pass


class OpenrouterConnector(BaseConnector):
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.getenv("openrouter_api_key")
        self.model = model or os.getenv("openrouter_model_name")

    def create_obj(self, structure: Any = None) -> ChatOpenAI:
        return ChatOpenAI(
            base_url="https://openrouter.ai/api/v1/",
            api_key=self.api_key,
            model=self.model,
        ).with_structured_output(structure, strict=True)

    def call(self, obj: ChatOpenAI, prompt: str) -> AIMessage:
        return obj.invoke(prompt)

    def acall(self, obj: ChatOpenAI, prompt: str) -> Coroutine:
        return obj.ainvoke(prompt)


class OllamaConnector(BaseConnector):
    def __init__(self, thinking: Literal["thinking", "non-thinking"], model: str | None = None) -> None:
        self.thinking = thinking
        if self.thinking == "non-thinking":
            self.model = model or os.getenv("ollama_model_name_non_thinking")
        else:
            self.model = model or os.getenv("ollama_model_name_thinking")

    def create_obj(self, structure: Any = None) -> ChatOllama:
        return ChatOllama(model=self.model).with_structured_output(structure)

    def call(self, obj: ChatOllama, prompt: str) -> AIMessage:
        return obj.invoke(prompt)

    def acall(self, obj: ChatOllama, prompt: str) -> Coroutine:
        return obj.ainvoke(prompt)


class GroqConnector(BaseConnector):
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.getenv("groq_api_key")
        self.model = model or os.getenv("groq_model_name")

    def create_obj(self, structure=None) -> ChatGroq:
        return ChatGroq(api_key=self.api_key, model=self.model).with_structured_output(structure, strict=True)

    def call(self, obj: ChatGroq, prompt: str) -> AIMessage:
        return obj.invoke(prompt)

    def acall(self, obj: ChatGroq, prompt: str) -> Coroutine:
        return obj.ainvoke(prompt)
