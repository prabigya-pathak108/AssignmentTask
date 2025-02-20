from utils.utilities_functions import UtilFunctionalities
from sql_gen.sql_generation_mechanism import SQLGenAndRetry
import json
import re


class ChatResponse:
    def __init__(self,provider :str ="gemini"):
        self.util_func=UtilFunctionalities()
        self.sql_gen_retry_instance=SQLGenAndRetry()
        self.provider=provider

    def intent_finder(self,question:str):
        try:
            kwargs={
                "user_question":question,
                "provider":self.provider
            }
            res=self.util_func.identify_sql_or_normal_text(kwargs=kwargs)
            json_str = re.search(r'```json\n(.*)\n```', res.content, re.DOTALL).group(1)

            print(res)
            json_data = json.loads(json_str)
            return json_data
        except Exception as e:
            print(e)
            return None

    def handle_chat(self,question : str):
        json_data=self.intent_finder(question)

        print(json_data)
        print("-----------------------------------------------")
        kwargs={
                        "user_question":question,
                        "provider":self.provider
                    }
        if json_data is None:
            result= self.sql_gen_retry_instance.sql_generation_and_execution(kwargs=kwargs)
            return result
        if (json_data.get("is_question_related_to_flight_delay_canellation",True)):
            result= self.sql_gen_retry_instance.sql_generation_and_execution(kwargs=kwargs)
            return result
        else:
            return {"data":json_data["response_message"]}

