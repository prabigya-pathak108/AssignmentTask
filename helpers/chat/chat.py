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

    def intent_finder(self,kwargs : dict):
        try:
            unique_id=kwargs.get("unique_id","")
            res=self.util_func.identify_sql_or_normal_text(kwargs=kwargs)
            json_data=res.content
            if isinstance(json_data,str):
                json_str = re.search(r'```json\n(.*)\n```', str(res.content).replace('\\n', '').replace('\\"', '"').replace("\{\{","{").replace("\}\}","\}"), re.DOTALL).group(1)
                json_data=json.loads(json_str)
            log_message(str(unique_id),"Intent Finding Success")
            return {"success":True,"json_data":json_data}
        except ValueError as e:
            log_message(str(unique_id),f"{str(e)}")
            return {"success":False,"json_data":{"response_message":f"{str(e)}"}}
        except Exception as e:
            log_message(str(unique_id),f"{str(e)}")
            return {"success":False,"json_data":{"response_message":"Sorry We cannot process that right now. Check you api key and model. Please Try again later."}}
        


    def handle_chat(self,question : str,unique_id:str,api_key: str=None,temperature:float=None,model:str=None):
        log_message(str(unique_id),"Chat Handler Initiated")
        kwargs={
                        "user_question":question,
                        "provider":self.provider,
                        "unique_id":unique_id,
                        "api_key":api_key,
                        "temperature":temperature,
                        "model":model
                    }
        json_data=self.intent_finder(kwargs=kwargs)

        if not json_data.get("success",False):
            return {"success":False,"data":json_data.get("json_data",{}).get("response_message","We are sorry, we cannot process that right now."),"is_sql":False}
        
        if (json_data.get("json_data",{}).get("is_question_related_to_flight_delay_canellation",True)):
            try:
                result= self.sql_gen_retry_instance.sql_generation_and_execution(kwargs=kwargs)
                return result
            except ValueError as e:
                log_message(str(unique_id),f"{str(e)}")
                return {"success":False,"data":f"{str(e)}","is_sql":False}
            except Exception as e:
                log_message(str(unique_id),f"{str(e)}")
                return {"success":False,"data":"Sorry We cannot process that right now.Check you api key and model. Please Try again later.","is_sql":False}
        else:
            return {"success":False,"data":json_data.get("json_data",{}).get("response_message","Sorry We cannot process that right now."),"is_sql":False}

