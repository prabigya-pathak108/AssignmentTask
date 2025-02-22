from helpers.utils.utilities_functions import UtilFunctionalities
from helpers.sql_gen.sql_generation_mechanism import SQLGenAndRetry
import json
import re
from helpers.logging_mechanism.logger import log_message


class ChatResponse:
    def __init__(self,provider :str ="gemini"):
        self.util_func=UtilFunctionalities()
        self.sql_gen_retry_instance=SQLGenAndRetry()
        self.provider=provider

    def intent_finder(self,question:str,unique_id):
        try:
            kwargs={
                "user_question":question,
                "provider":self.provider
            }
            res=self.util_func.identify_sql_or_normal_text(kwargs=kwargs)
            json_data=res.content
            if isinstance(json_data,str):
                json_str = re.search(r'```json\n(.*)\n```', str(res.content).replace('\\n', '').replace('\\"', '"'), re.DOTALL).group(1)
                json_data=json.loads(json_str)
            # json_str = re.search(r'```json\n(.*)\n```', res.content, re.DOTALL).group(1)
            # json_data = json.loads(json_str)
            log_message(str(unique_id),"Intent Finding Success")
            return {"success":True,"json_data":json_data}
        except Exception as e:
            log_message(str(unique_id),f"Error Occured while Finding Intent: {str(e)}")
            return {"success":False,"json_data":{}}

    def handle_chat(self,question : str,unique_id:str):
        log_message(str(unique_id),"Chat Handler Initiated")
        json_data=self.intent_finder(question,unique_id)

        print(json_data)
        print("-----------------------------------------------")
        kwargs={
                        "user_question":question,
                        "provider":self.provider,
                        "unique_id":unique_id
                    }
        if not json_data["success"]:
            result= self.sql_gen_retry_instance.sql_generation_and_execution(kwargs=kwargs)
            return result
        if (json_data.get("json_data",{}).get("is_question_related_to_flight_delay_canellation",True)):
            result= self.sql_gen_retry_instance.sql_generation_and_execution(kwargs=kwargs)
            return result
        else:
            return {"data":json_data.get("json_data",{}).get("response_message","Sorry We cannot process that right now."),"is_sql":False}

