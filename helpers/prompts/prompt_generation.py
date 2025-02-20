from .base import BasePrompt
import os
import json


class PromptGenerationClass(BasePrompt):
    current_dir = os.path.dirname(os.path.abspath(__file__))

    def get_prompt(self,prompt_type):
        try:
            _prompt_path = os.path.join(self.current_dir,"assets" ,f"{prompt_type}.tmpl")
            if os.path.exists(_prompt_path):
                with open(_prompt_path, "r") as file:
                    prompt = file.read()
                return prompt
            else:
                raise ValueError(f"Erro prompt type")
        except Exception as e:
            raise RuntimeError(f"Error getting prompt: {e}")
    
    def set_var(self, prompt, vars):
        for key, value in vars.items():
            prompt = prompt.replace(f"{{{key}}}", value)
        return prompt