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
        """
        Constructor for GroqLLM.

        Args:
            api_key (str): The api key for the Groq model.
            temperature (float): The temperature for the Groq model.
            model_name (str): The name of the Groq model.
        """
        self.__api_key = api_key
        self.temperature = temperature
        self.model_name = model_name
        self.llm = self.get_llm()
    
    def get_llm(self):
        """
        Initializes and returns a ChatGroq instance configured with the provided API key,
        temperature, and model name.

        Returns:
            ChatGroq: An instance of the ChatGroq class configured with the specified parameters.
        """

        return ChatGroq(api_key=self.__api_key,temperature=self.temperature, model_name=self.model_name)

    def invoke_llm(self, prompt):
        """
        Invokes the Groq LLM with the given prompt.

        Args:
            prompt (str): The prompt to send to the LLM.

        Returns:
            str: The response from the LLM.

        Raises:
            ValueError: If there is an error invoking the LLM.
        """
        try:
            return self.llm.invoke(prompt)
        except:
           raise ValueError("Error in Invoking LLM. Check your API and model.")

class GeminiLLM(BaseLLM):
    def __init__(self, api_key, temperature, model_name):
        """
        Constructor for GeminiLLM.

        Args:
            api_key (str): The api key for the Gemini model.
            temperature (float): The temperature for the Gemini model.
            model_name (str): The name of the Gemini model.
        """
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
            raise ValueError("Error in Invoking LLM. Check your API and model.")
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
            raise ValueError("Error in Invoking LLM. Check your API and model.")

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
            raise ValueError("Error in Invoking LLM. Check your API and model.")



def initialize_llm_from_factory(provider, temperature=None, api_key=None, model=None):
    """Returns an LLM instance based on the provider name."""
    if api_key is None:
        api_key = secret_manager.get_from_env(f"{provider.upper()}_API_KEY")
        if api_key is None:
            raise ValueError(f"API key for {provider} is required but not provided or found in .env")
    if temperature is None:
        temperature = 0.1
    else:
        if not isinstance(temperature, (int, float)) or not (0 <= temperature <= 1):
            raise ValueError("Temperature must be a number between 0 and 1.")

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
