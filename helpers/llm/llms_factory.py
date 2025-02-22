from helpers.secret_manager.secrets import SecretManager
from .base import BaseLLM


from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import HuggingFaceHub, LLMChain


secret_manager = SecretManager()

# Import LLM classes
class GroqLLM(BaseLLM):
    def __init__(self, api_key, temperature, model_name):
        self.__api_key = api_key
        self.temperature = temperature
        self.model_name = model_name
        self.llm = self.get_llm()
    
    def get_llm(self):
        return ChatGroq(api_key=self.__api_key,temperature=self.temperature, model_name=self.model_name)

    def invoke_llm(self, prompt):
        try:
            return self.llm.invoke(prompt)
        except:
            print("Error")

class GeminiLLM(BaseLLM):
    def __init__(self, api_key, temperature, model_name):
        self.__api_key = api_key
        self.temperature = temperature
        self.model_name = model_name
        self.llm = self.get_llm()
    
    def get_llm(self):
        return ChatGoogleGenerativeAI(api_key=self.__api_key,temperature=self.temperature, model=self.model_name)

    def invoke_llm(self, prompt):
        try:
            return self.llm.invoke(prompt)
        except Exception as e:
            print("Error: ",e)
class HuggingFaceLLM(BaseLLM):
    def __init__(self, api_key, temperature, model_name):
        self.__api_key = api_key
        self.temperature = temperature
        self.model_name = model_name
        self.llm = self.get_llm()
    
    def get_llm(self):
        return HuggingFaceHub(repo_id=self.model_name, huggingfacehub_api_token= self.__api_key,
                                        model_kwargs={"temperature":self.temperature})

    def invoke_llm(self, prompt):
        try:
            return self.llm.invoke(prompt)
        except:
            print("Error")

class OpenAILLM(BaseLLM):
    def __init__(self, api_key, temperature, model_name):
        self.__api_key = api_key
        self.temperature = temperature
        self.model_name = model_name
        self.llm = self.get_llm()
    
    def get_llm(self):
        return ChatOpenAI(api_key=self.__api_key,temperature=self.temperature, model=self.model_name)

    def invoke_llm(self, prompt):
        try:
            return self.llm.invoke(prompt)
        except:
            print("Error")



def initialize_llm_from_factory(provider, temperature=None, api_key=None, model=None):
    """Returns an LLM instance based on the provider name."""
    if api_key is None:
        api_key = secret_manager.get_from_env(f"{provider.upper()}_API_KEY")
        if api_key is None:
            raise ValueError(f"API key for {provider} is required but not provided or found in .env")
    print("--------Provider hererererererere:",provider)
    if temperature is None:
        temperature = 0.1

    if model is None:
        model = secret_manager.get_from_env(f"{provider.upper()}_MODEL")
        if model is None:
            raise ValueError(f"Model for {provider} is required but not provided or found in .env")

    if provider == "groq":
        return GroqLLM(
            api_key=api_key,
            temperature=temperature,
            model_name=model
        )
    elif provider == "gemini":
        return GeminiLLM(
            api_key=api_key,
            temperature=temperature,
            model_name=model
        )
    elif provider == "huggingface":
        return HuggingFaceLLM(
            api_key=api_key,
            temperature=temperature,
            model_name=model
        )
    elif provider == "openai":
        return OpenAILLM(
            api_key=api_key,
            temperature=temperature,
            model_name=model
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}")
