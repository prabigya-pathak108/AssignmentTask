from abc import ABC, abstractmethod


class BaseLLM(ABC):
    @abstractmethod
    def get_llm(self):
        NotImplementedError

    @abstractmethod
    def invoke_llm(self, prompt: str):
        NotImplementedError