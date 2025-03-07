import unittest
import sys
import os
import random
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from helpers.chat.chat import ChatResponse
from helpers.secret_manager.secrets import SecretManager
from helpers.sql_gen.sql_generation_mechanism import SQLGenAndRetry
from helpers.logging_mechanism.logger import log_message
import uuid
import time

class TestSQLGenerator(unittest.TestCase):
    def __init__(self, methodName = "runTest"):
        self.manager = SecretManager()
        self.sql_validator = SQLGenAndRetry()

    def test_valid_sql_generation(self, **kwargs):
        """
        A test function to generate valid SQL using a language learning model (LLM).

        Args:
            **kwargs (dict): A dictionary containing the following parameters:
                - provider (str): The LLM provider name (e.g., "gemini").
                - user_question (str): The user's question.
                - api_key (str): The API key for the LLM provider.
                - temperature (float): The temperature setting for LLM query generation.
                - model (str): The model name to be used with the LLM.

        Returns:
            dict: A dictionary containing the response message, success status, and retry indication.
        """
        inst=ChatResponse(provider=kwargs.get("provider","gemini"))
        question= kwargs.get("user_question")
        api_key=kwargs.get("api_key")
        temperature=kwargs.get("temperature")
        model=kwargs.get("model")
        unique_id=str(uuid.uuid4())
        res=inst.handle_chat(question=question,unique_id=unique_id,api_key=api_key,temperature=temperature,model=model)
        return res
    
    def tet_sql_generation_from_file(self):
        
        """
        A test function to generate SQL from a list of questions stored in a JSON file.

        This function reads a JSON file containing a list of questions and their expected responses.
        It then uses the test_valid_sql_generation function to generate SQL for each question using
        a language learning model (LLM). The generated SQL is then added to the JSON file.

        Args:
            None

        Returns:
            None
        """
        file_path = os.path.join("test", "questions.json")
        with open(file_path, "r") as file:
            json_data = json.load(file)
        for data in json_data:
            question=json_data[data]["question"]
            providers=["groq","gemini"]
            for provider in providers:
                if str(f"{provider}_response") not in json_data[data].keys():
                    temperature=0.1
                    num_val=random.randint(1,4)
                    
                    time.sleep(1)
                    if provider=="gemini":
                        api_key=self.manager.get_from_env(f"{str(provider).upper()}_API_KEY{str(num_val)}")
                    else:
                        api_key=self.manager.get_from_env(f"{str(provider).upper()}_API_KEY")
                    
                    model=self.manager.get_from_env(f"{str(provider).upper()}_MODEL")

                    json_body={
                        "provider":provider,
                        "user_question":question,
                        "api_key":api_key,
                        "temperature":temperature,
                        "model":model
                    }
                    res=self.test_valid_sql_generation(**json_body)
                    json_data[data][str(f"{provider}_response")]=res
                    with open(file_path,"w+") as f:
                        json.dump(json_data,f,indent=2)
        
    def test_sql_execution_from_file(self):
        """
        A test function to execute a list of SQLs from a JSON file and log the results.

        This function reads a JSON file containing a list of SQLs and their expected execution status.
        It then executes each SQL using the sql_execution method of the SQLValidator class.
        The execution status and report are logged to a file.

        Args:
            None

        Returns:
            None
        """
        file_path = os.path.join("test", "sqls_execution.json")
        with open(file_path, "r") as file:
            data = json.load(file)

        for entry in data:
            for key, value in entry.items():
                unique_id = str(uuid.uuid4())
                log_message(unique_id, f"Testing SQL: {value['sql']}")
                report = self.sql_validator.sql_execution(value["sql"], unique_id)

                value["sql_execution_status"] = report["success"]
                value["sql_execution_report"] = report["data"]
                if report["error_msg"]:
                    value["error_message"] = report["error_msg"]

                self.assertTrue(report["success"], msg=f"SQL failed: {report['error_msg']}")

        with open(file_path, "w") as file:
            json.dump(data, file, indent=2)


