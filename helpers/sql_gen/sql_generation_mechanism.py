from .base import SQLBaseClass
from prompts.prompt_generation import PromptGenerationClass
from llm.llms_factory import initialize_llm_from_factory
import random
import os
import json
import yaml
from sqlalchemy.exc import SQLAlchemyError
from database_work_model import database as db
from sqlalchemy import text


class SQLGenAndRetry(SQLBaseClass):
    def __init__(self):
        super().__init__()
        self.prompt_factory = PromptGenerationClass()
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.__questions_pair=self.__read_json_file()
        self.schema=self.__read_schema_file()

    def __read_json_file(self):
         __prompt_path = os.path.join(self.current_dir,"assets" ,"question_sql.json")
         with open(__prompt_path, "r") as file:
            qa_list = json.load(file)
         return qa_list
    
    def __read_schema_file(self):
        __schema_path = os.path.join(self.current_dir,"assets" ,"schema.yaml")
        with open(__schema_path, "r") as file:
            schema_data = yaml.safe_load(file)
        return schema_data

    
    def sql_execution(self, generated_sql):
        extracted_sql= self.extract_sql_from_llm_response(generated_sql)
        if self.validating_sql_and_select_only(extracted_sql)=="Not allowed":
            return {"success":False,"retry":False,"data":"Kindly you cannot perform database changing operations. You can only retrieve records. Thank you for consideration...","error_msg":None}
        db_s = next(db.get_db())  # Get DB session
        try:
            result = db_s.execute(text(extracted_sql))  # Wrap SQL query with text()
            data = result.fetchall()  # Fetch results

            if data:  # If data is retrieved, exit loop
                return {"success":True,"retry":False,"data":data}
            else:
                return {"success":True,"retry":False,"data":"The database currently doesnot have any infomation regarding your question. Thank you for convenience","error_msg":None}

        except SQLAlchemyError as e:
            error_message = "\n".join(x for x in str(e).split("\n")[:-2])
            return {"success":False,"retry":True,"data":None,"error_msg":error_message}
        finally:
            db_s.close()

        

    def _generate_sql_prompt(self, llm, prompt_type, **kwargs):
        """Helper method to generate SQL or error-handling prompts dynamically."""
        prompt_template = self.prompt_factory.get_prompt(prompt_type)
        question = str(kwargs.get("kwargs",{}).get("user_question", ""))
        few_shots_questions = random.choices(self.__questions_pair, k=2)
        print("I am herer")
        print(kwargs)
        print("Now: ",question)
        query = {
            "question": question,
            "schemas": str(self.schema),
            "few_shot_examples": str(few_shots_questions)
        }

        if prompt_type == "error_handle_prompt":
            query["errors_encountered"] = str(kwargs.get("list_of_errors", []))

        formatted_prompt = self.prompt_factory.set_var(prompt_template, query)
        print("formatted_prompt",str(formatted_prompt))
        print("type: ",type(formatted_prompt))

        try:
            response = llm.invoke_llm(formatted_prompt)
            return {"success":True,"sql_generated":response.content if response else None,"error":None}
        except Exception as e:
            return {"success":False,"sql_generated":None,"error":str(e)}

    def sql_generation(self, llm, **kwargs):
        return self._generate_sql_prompt(llm, "sql_generation_prompt", **kwargs)

    def retry_mechanism(self, llm, list_of_errors, **kwargs):
        return self._generate_sql_prompt(llm, "error_handle_prompt", list_of_errors=list_of_errors, **kwargs)

    def sql_generation_and_execution(self, **kwargs):
        llm = initialize_llm_from_factory(provider=kwargs.get("kwargs",{}).get("provider", "gemini"))

        max_retries = 3
        list_of_errors = []  # Store errors for retry mechanism

        for attempt in range(max_retries):
            if attempt == 0:
                generated_sql = self.sql_generation(llm, **kwargs)
            else:
                generated_sql = self.retry_mechanism(llm, list_of_errors, last_failed_sql=generated_sql["sql_generated"], **kwargs)

            print("SQL Gen: ",generated_sql["sql_generated"])
            if not generated_sql["success"]:
                return {"data": generated_sql["error"]}
            

            execution_result = self.sql_execution(generated_sql["sql_generated"])

            if execution_result["success"]:
                return {"data": execution_result["data"],"generated_sql":generated_sql["sql_generated"]}

            # Store error for retry prompt
            list_of_errors.append(str(generated_sql["sql_generated"]+"\n"+execution_result["error_msg"]+"\n\n"))
            # print(f"Retrying SQL execution... Attempt {attempt + 1}/{max_retries}")
            

        return {"success": False, "retry": False, "data": "Sorry The data could not be retrieved", "error_msg": "Max retries reached."}





