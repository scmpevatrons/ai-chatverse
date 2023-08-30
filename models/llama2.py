"""
LLAMA2 model
"""
from typing import Dict, Any, Optional
from langchain.llms import LlamaCpp
from models.base_langchain_model import BaseLangChainModel


class LLAMA2(BaseLangChainModel):
    """
    This is the class for the LLAMA2 model
    """
    def __init__(self, system_message: Optional[str] = None,
                 memory_kvargs:Dict[Any, Any]=None,
                 **kvargs) -> None:
        """
        This is the constructor for the LLAMA2 class

        Args:
            system_message: The system message to give to the LLM
            memory_kvargs: The kvarguments for the memory
            **kvargs: The arguments for the LLM
        """
        super().__init__(LlamaCpp, system_message, memory_kvargs, **kvargs)
