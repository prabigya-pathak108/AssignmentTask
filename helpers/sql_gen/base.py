import json
import os
import re
import sqlite3
import traceback
from abc import ABC, abstractmethod
from typing import List, Tuple, Union
from urllib.parse import urlparse
from helpers.secret_manager.secrets import SecretManager

import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
import requests
import sqlparse
import sqlparse
import re



class SQLBaseClass:
    def __init__(self):
        self.manager_config=SecretManager()
        
    @abstractmethod
    def sql_generation(self,**kwargs):
        pass

    def sql_execution(self,generated_sql):
        pass

    @abstractmethod
    def retry_mechanism(self,**kwargs):
        pass

    def extract_sql_from_llm_response(self,llm_response: str) -> str:
        """
        Extracts the SQL query from the LLM response. This is useful in case the LLM response contains other information besides the SQL query.
        Args:
            llm_response (str): The LLM response.
        Returns:
            str: The extracted SQL query.
        """

        # For CTE
        sqls = re.findall(r"\bWITH\b .*?;", llm_response, re.DOTALL)
        if sqls:
            sql = sqls[-1]
            return sql

        # If the llm_response is not markdown formatted, extract last sql by finding select and ; in the response
        sqls = re.findall(r"SELECT.*?;", llm_response, re.DOTALL)
        if sqls:
            sql = sqls[-1]
            return sql

        # If the llm_response contains a markdown code block, with or without the sql tag, extract the last sql from it
        sqls = re.findall(r"```sql\n(.*)```", llm_response, re.DOTALL)
        if sqls:
            sql = sqls[-1]
            return sql

        sqls = re.findall(r"```(.*)```", llm_response, re.DOTALL)
        if sqls:
            sql = sqls[-1]
            return sql

        return llm_response

    def validating_sql_and_select_only(self,sql: str) -> bool:
            """
            Checks if the SQL query is valid. This is usually used to check if we should run the SQL query or not.
            By default it checks if the SQL query is a SELECT statement. Allowing only SELECT method

            Args:
                sql (str): The SQL query to check.

            Returns:
                bool: True if the SQL query is valid, False otherwise.
            """
            parsed = sqlparse.parse(sql)
            for statement in parsed:
                if statement.get_type() not in ['SELECT']:
                    return "Not allowed"
            return "Allowed Method"

