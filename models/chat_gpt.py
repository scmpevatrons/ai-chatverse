"""
ChatGPT is a class that inherits from BaseLangChainModel and uses 
the ChatOpenAI class to generate text.
"""
from typing import Dict, Any, Optional
from langchain.chat_models import ChatOpenAI
from models.base_langchain_model import BaseLangChainModel


class ChatGPT(BaseLangChainModel):
    """
    This is the class for the ChatGPT model
    """
    def __init__(self, system_message:Optional[str] = None,
                 memory_kvargs:Dict[Any, Any]=None, **kvargs) -> None:
        """
        This is the constructor for the ChatGPT class
        
        Args:
            system_message: The system message to give to the LLM
            memory_kvargs: The kvarguments for the memory
            **kvargs: The arguments for the LLM
        """
        super().__init__(ChatOpenAI, system_message,
                         memory_kvargs, **kvargs)
