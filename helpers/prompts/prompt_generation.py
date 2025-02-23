from .base import BasePrompt
import os
import json


class PromptGenerationClass(BasePrompt):
    current_dir = os.path.dirname(os.path.abspath(__file__))

    def get_prompt(self,prompt_type):
        """
        Retrieve a prompt from the assets directory based on the given type.

        Args:
            prompt_type (str): The type of prompt to retrieve.

        Returns:
            str: The content of the prompt file as a string.

        Raises:
            ValueError: If the prompt type is invalid.
            RuntimeError: If there is an error getting the prompt.
        """
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
        """
        Replace placeholders in the given prompt with the given vars.

        Args:
            prompt (str): The prompt string with placeholders in the format of {{key}}.
            vars (dict): A dictionary of key-value pairs to replace the placeholders.

        Returns:
            str: The prompt string with placeholders replaced.
        """
        for key, value in vars.items():
            prompt = prompt.replace(f"{{{key}}}", value)
        return prompt