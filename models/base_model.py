"""
This file contains the base model class that all models should inherit from
"""
from typing import  List, Optional
from datetime import datetime
from langchain.callbacks.base import BaseCallbackHandler
from schema.message import Message

#pylint: disable=too-few-public-methods
class FakeLLM:
    """
    This is a fake LLM class that is used for testing
    """

    def __init__(self, **kvargs) -> None:
        """
        This is the constructor for the FakeLLM class
        
        Args:
            **kvargs: The arguments for the LLM
        """

    # pylint: disable=unused-argument
    def give_response_to_prompt(self, messages:List[Message], system_prompt:str)->str:
        """
        This method is used to give a response to a prompt
        
        Args:
            messages: The messages to give to the LLM
            system_prompt: The system prompt to give to the LLM
        
        Returns:
            The response from the LLM
        """
        return "This is a fake response"


class BaseLLMModel:
    """
    This is the base model class that all models should inherit from
    """

    def __init__(self, system_message:Optional[str]=None, **kvargs) -> None:
        """
        This is the constructor for the BaseLLMModel class
        
        Args:
            system_message: The system message to give to the LLM
            **kvargs: The arguments for the LLM
        """
        self.system_message = system_message
        self.llm = FakeLLM(**kvargs)
        self.messages = []


    def get_prompt_response(self, message:str,
                            stream_handler:Optional[BaseCallbackHandler]=None)->str:
        """
        This method is used to get a response to a prompt
        
        Args:
            message: The message to give to the LLM
            stream_handler: if passed response is streamed via handler
        
        Returns:
            The response from the LLM
        """
        self.add_user_message(message=message)
        if stream_handler:
            raise NotImplementedError("This Model does not have streaming capabilities")
        ai_response = self.llm.give_response_to_prompt(messages=self.messages,
                                                       system_prompt=self.system_message)
        self.add_ai_message(message=ai_response)
        return ai_response


    def get_prompt_response_without_memory(self, message:str,
                                           stream_handler:Optional[BaseCallbackHandler]=None)->str:
        """
        This method is used to get a response to a prompt
        The message is given to the LLM without any memory
        
        Args:
            message: The message to give to the LLM
            stream_handler: if passed response is streamed via handler
        
        Returns:
            The response from the LLM
        """
        if stream_handler:
            raise NotImplementedError("This Model does not have streaming capabilities")
        return self.llm.give_response_to_prompt(messages=[message], system_prompt=None)


    def add_ai_message(self, message:str):
        """
        This method is used to add an AI message to the conversation
        
        Args:
            message: The message to add to the conversation
        """
        self.messages.append(Message(message=message, message_type='AI', timestamp=datetime.now()))


    def add_user_message(self, message:str):
        """
        This method is used to add a user message to the conversation
        
        Args:
            message: The message to add to the conversation
        """
        self.messages.append(Message(message=message, message_type='USER', 
                                     timestamp=datetime.now()))


    def get_messages(self)->List[Message]:
        """
        This method is used to get the messages in the conversation
        
        Returns:
            The messages in the conversation
        """
        return self.messages
