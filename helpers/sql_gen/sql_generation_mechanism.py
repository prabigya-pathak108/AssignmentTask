from .base import SQLBaseClass
from helpers.prompts.prompt_generation import PromptGenerationClass
from helpers.llm.llms_factory import initialize_llm_from_factory
import random
import os
import json
import yaml
from sqlalchemy.exc import SQLAlchemyError
from helpers.database_work_model import database as db
from sqlalchemy import text
from helpers.logging_mechanism.logger import log_message


class SQLGenAndRetry(SQLBaseClass):
    def __init__(self):
        super().__init__()
        self.prompt_factory = PromptGenerationClass()
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.__questions_pair=self.__read_json_file()
        self.schema=self.__read_schema_file()

    def __read_json_file(self):
        """Reads question_sql.json file from assets directory and returns list of questions and sql pair."""
        __prompt_path = os.path.join(self.current_dir,"assets" ,"question_sql.json")
        with open(__prompt_path, "r") as file:
            qa_list = json.load(file)
        return qa_list
    
    def __read_schema_file(self):
        """Reads schema.yaml file from assets directory and returns schema data.
        Schema contains information about the tables and their respective columns in the database."""
        __schema_path = os.path.join(self.current_dir,"assets" ,"schema.yaml")
        with open(__schema_path, "r") as file:
            schema_data = yaml.safe_load(file)
        return schema_data

    
    def sql_execution(self, generated_sql,unique_id):
        """
    Executes the provided SQL query after validating it to ensure it is a safe sql statement.

    Args:
        generated_sql (str): The generated SQL query to be executed.
        unique_id (str): A unique identifier for logging purposes.

    Returns:
        dict: A dictionary containing the result of the SQL execution, including success status, retry indication,
              data or error message. If the SQL method is not allowed, returns an appropriate message with retry as False.
              If successful, returns a success message and data if available. In case of execution errors, returns the 
              error message and sets retry to True.

    Logs:
        Logs various stages of SQL execution, including successful database connection, execution success, and errors 
        encountered during execution.
    """

        extracted_sql= self.extract_sql_from_llm_response(generated_sql)
        if self.validating_sql_and_select_only(extracted_sql)=="Not allowed":
            log_message(str(unique_id),f"SQL method Not Allowed",level="warning")
            return {"success":False,"retry":False,"data":"Kindly you cannot perform database changing operations. You can only retrieve records. Thank you for consideration...","error_msg":"SQL method Not Allowed"}
        
        try:
            db_s = next(db.get_db())  # Get DB session
            log_message(str(unique_id),f"Database instance created successfully")
            result = db_s.execute(text(extracted_sql))  # Wrap SQL query with text()
            data = result.fetchall()  # Fetch results
            log_message(str(unique_id),f"SQL execution success")

            if data:  # If data is retrieved, exit loop
                return {"success":True,"retry":False,"data":"SQL Execution Success","error_msg":None}
            else:
                return {"success":True,"retry":False,"data":"The database currently doesnot have any infomation regarding your question. Thank you for convenience","error_msg":None}

        except SQLAlchemyError as e:
            error_message = "\n".join(x for x in str(e).split("\n")[:-2])
            log_message(str(unique_id),f"SQL execution unsuccess {error_message}")
            return {"success":False,"retry":True,"data":None,"error_msg":error_message}
        finally:
            db_s.close()

        

    def _generate_sql_prompt(self, llm, prompt_type, **kwargs):
        """Helper method to generate SQL or error-handling prompts dynamically."""
        prompt_template = self.prompt_factory.get_prompt(prompt_type)
        question = str(kwargs.get("kwargs",{}).get("user_question", ""))
        few_shots_questions = random.choices(self.__questions_pair, k=2)
        #print("I am herer")
        #print(kwargs)
        #print("Now: ",question)
        query = {
            "question": question,
            "schemas": str(self.schema),
            "few_shot_examples": str(few_shots_questions)
        }
        unique_id=kwargs.get("unique_id",'')

        if prompt_type == "error_handle_prompt":
            query["errors_encountered"] = str(kwargs.get("list_of_errors", []))

        formatted_prompt = self.prompt_factory.set_var(prompt_template, query)
        # #print("formatted_prompt",str(formatted_prompt))
        # #print("type: ",type(formatted_prompt))

        try:
            response = llm.invoke_llm(formatted_prompt)
            log_message(str(unique_id),f"Successfully Invoked llm{str(response)}")
            return {"success":True,"sql_generated":response.content if response else None,"error":None}
        except Exception as e:
            log_message(str(unique_id),f"Failure in LLM invoke: {str(response)}")
            return {"success":False,"sql_generated":None,"error":str(e)}

    def sql_generation(self, llm, **kwargs):
        return self._generate_sql_prompt(llm, "sql_generation_prompt", **kwargs)

    def retry_mechanism(self, llm, list_of_errors, **kwargs):
        return self._generate_sql_prompt(llm, "error_handle_prompt", list_of_errors=list_of_errors, **kwargs)

    def sql_generation_and_execution(self, **kwargs):
        """
    Generates and executes SQL queries using a language learning model (LLM) with retry mechanisms.

    This method initializes an LLM instance based on the provided parameters, generates SQL queries,
    and attempts to execute them. If the SQL query generation or execution fails, it retries up to a
    maximum number of attempts. Successful SQL execution returns the generated SQL and data, while
    failures and non-retryable errors are logged and returned.

    Args:
        **kwargs: Arbitrary keyword arguments including:
            - provider (str): The LLM provider name (e.g., "gemini").
            - api_key (str): The API key for the LLM provider.
            - model (str): The model name to be used with the LLM.
            - temperature (float): The temperature setting for LLM query generation.
            - unique_id (str): A unique identifier for logging purposes.

    Returns:
        dict: A dictionary with the following keys:
            - success (bool): Indicates if the SQL generation and execution were successful.
            - data (str): The generated SQL query or error message.
            - is_sql (bool): Indicates if the returned data is a valid SQL query.
            - error_msg (str, optional): Error message if the operation fails.

    Logs:
        Logs various stages of SQL generation and execution, including success, failure, and retry
        attempts.
    """

        llm = initialize_llm_from_factory(provider=kwargs.get("kwargs",{}).get("provider", "gemini"),api_key=kwargs.get("kwargs",{}).get("api_key", None),model=kwargs.get("kwargs",{}).get("model", None),temperature=kwargs.get("kwargs",{}).get("temperature", None))
        try:
            llm = initialize_llm_from_factory(provider=kwargs.get("kwargs",{}).get("provider", "gemini"),api_key=kwargs.get("kwargs",{}).get("api_key", None),model=kwargs.get("kwargs",{}).get("model", None),temperature=kwargs.get("kwargs",{}).get("temperature", None))
        except ValueError as e:
            raise ValueError(f"{e}")
        
        unique_id=kwargs.get("kwargs",{}).get("unique_id", "")
        max_retries = 3
        list_of_errors = []  # Store errors for retry mechanism

        for attempt in range(max_retries):
            if attempt == 0:
                generated_sql = self.sql_generation(llm, **kwargs)
            else:
                generated_sql = self.retry_mechanism(llm, list_of_errors, last_failed_sql=generated_sql["sql_generated"], **kwargs)

            #print("SQL Gen: ",generated_sql["sql_generated"])
            if not generated_sql["success"]:
                log_message(str(unique_id),f"SQL Generation UnSuccessful: Attempting Execution: Attempt{attempt}")
                list_of_errors.append(str(generated_sql["error"]))
                continue
            
            log_message(str(unique_id),f"SQL Generation Successful: Attempting Execution: Attempt{attempt}")
            execution_result = self.sql_execution(generated_sql["sql_generated"],unique_id)
            
            # Check if SQL execution was successful, and if it is successful then return the SQL, invalid SQL will not executed
            if execution_result["success"]:
                # return {"data": execution_result["data"],"generated_sql":generated_sql["sql_generated"]}
                log_message(str(unique_id),f"SQL Generation Success. Returning Final SQl")
                log_message(str(unique_id),str(generated_sql["sql_generated"]))
                return {"success": True,"data":generated_sql["sql_generated"],"is_sql":True}
            
            # If the SQL query asked by user is not allowed, then return the error message
            if not execution_result["retry"]:
                return execution_result

            # Store error for retry prompt
            list_of_errors.append(str(generated_sql["sql_generated"]+"\n"+str(execution_result["error_msg"])+"\n\n"))
            # #print(f"Retrying SQL execution... Attempt {attempt + 1}/{max_retries}")
            
        log_message(str(unique_id),f"SQL Generation Unsuccessful: Maximum Retries Acheived")
        return {"success": False,  "data": "Sorry The data could not be retrieved", "error_msg": "Max retries reached.","is_sql":False}





