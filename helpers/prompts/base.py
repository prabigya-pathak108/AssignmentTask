from abc import ABC, abstractmethod


class BasePrompt(ABC):
    _prompt_url = None

    @abstractmethod
    def get_prompt(self, *args, **kwargs):
        pass
    
    @abstractmethod
    def set_var(self, prompt: str, vars: dict):
        pass