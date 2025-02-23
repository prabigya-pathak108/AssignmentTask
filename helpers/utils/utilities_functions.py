from helpers.llm.llms_factory import initialize_llm_from_factory
from helpers.prompts.prompt_generation import PromptGenerationClass

from typing import List,Generic, Optional
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser


class IntentIdentificationMgmt(BaseModel):
    is_question_related_to_flight_delay_canellation:  bool = Field(description="boolean value to indicate if user question relates to flight delay and cancellation dataset")
    response_message: Optional[str] = Field(
        default=None, 
        description="The response message related to the conversational query like hello, hi, etc,."
    )


class UtilFunctionalities:
    def __init__(self):
        self.prompt_factory = PromptGenerationClass()
    
    def identify_sql_or_normal_text(self,**kwargs):
        prompt_template = self.prompt_factory.get_prompt("identify_sql_or_normal_text")
        provider= str(kwargs.get("kwargs",{}).get("provider", "gemini"))
        question = str(kwargs.get("kwargs",{}).get("user_question", ""))
        print("provider is: ",provider)
        print("kwargs: ",kwargs)
        try:
            llm = initialize_llm_from_factory(provider=provider,api_key=kwargs.get("kwargs",{}).get("api_key", None),model=kwargs.get("kwargs",{}).get("model", None),temperature=kwargs.get("kwargs",{}).get("temperature", None))
        except ValueError as e:
            raise ValueError(f"{e}")  
        intent_generation_parser = PydanticOutputParser(pydantic_object=IntentIdentificationMgmt)

        
        query = {
            "question": question,
            "format_instructions":intent_generation_parser.get_format_instructions()
        }
        formatted_prompt = self.prompt_factory.set_var(prompt_template, query)
        print("********************************************************")
        try:
            response = llm.invoke_llm(formatted_prompt)
            print(response)
            return response
        except ValueError as e:
            raise ValueError(f"Invalid API key or model name. Please check and retry.")  
        
