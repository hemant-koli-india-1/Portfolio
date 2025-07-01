from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate


class Chain:
    def __init__(self, groq_api_key: str):
        """
        Initialize the Chain with Groq LLM.
        
        Args:
            groq_api_key (str): Your Groq API key for authentication
        """
        self.llm = ChatGroq(
            temperature=0,
            groq_api_key=groq_api_key,
            model_name="meta-llama/llama-4-scout-17b-16e-instruct"
        )

    def ask(self, prompt: str, input_vars: dict) -> str:
        """
        Generate a response based on the input prompt and variables.
        
        Args:
            prompt (str): The prompt template string
            input_vars (dict): Dictionary of variables to format the prompt
            
        Returns:
            str: The generated response
        """
        prompt_template = PromptTemplate(
            input_variables=list(input_vars.keys()), 
            template=prompt
        )
        chain = prompt_template | self.llm
        response = chain.invoke(input_vars)
        return response.content.strip()

    def __call__(self, prompt: str, **kwargs) -> str:
        """
        Make the Chain instance callable for backward compatibility.
        
        Args:
            prompt (str): The prompt to generate a response for
            **kwargs: Additional arguments to pass to the ask method
            
        Returns:
            str: The generated response
        """
        return self.ask(prompt, kwargs)
