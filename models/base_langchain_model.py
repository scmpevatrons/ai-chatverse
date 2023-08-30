"""
This module implements the base class for all LangChain models
"""
from typing import Dict, Any, Union, Optional
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chat_models.base import BaseChatModel
from langchain import PromptTemplate
from langchain.llms.base import LLM
from langchain.chat_models.base import SimpleChatModel
from langchain.llms.fake import FakeListLLM
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import LLMChain
from langchain.schema.messages import SystemMessage, HumanMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
import streamlit as st
from models.base_model import BaseLLMModel


#pylint: disable=abstract-method
class StreamlitDisplayHandler(BaseCallbackHandler):
    """
    This class is used to display the output of the LLM in streamlit
    """
    def __init__(self, container:st.container, initial_text:str="", display_method:str='markdown'):
        """
        This is the constructor for the StreamlitDisplayHandler class

        Args:
            container: The streamlit container to display the output in
            initial_text: The initial text to display
            display_method: The method to use to display the text
        """
        self.container = container
        self.text = initial_text
        self.display_method = display_method


    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """
        This method is used to display the output of the LLM in streamlit
        
        Args:
            token: The newly generated token
            **kwargs: The keyword arguments
        """
        self.text += token
        display_function = getattr(self.container, self.display_method, None)
        if display_function is not None:
            display_function(self.text+"▌")
        else:
            raise ValueError(f"Invalid display_method: {self.display_method}")


    def on_llm_end(self, response:str, **kwargs) -> None:
        """
        This method is used to display the output of the LLM in streamlit
        Args:
            response: The response from the LLM
            **kwargs: The keyword arguments
        """
        self.text = ""


class BaseLangChainModel(BaseLLMModel):
    """
    This is the base class for all LangChain models
    """

    def __init__(self, llm:Union[LLM, SimpleChatModel]=None,
                 system_message:Optional[str]=None,
                 memory_kvargs:Dict[Any, Any]=None,
                 **kvargs) -> None:
        """
        This is the constructor for the BaseLangChainModel class
        
        Args:
            llm: The Langchain Language Model
            system_message: The system message to display
            memory_kvargs: The keyword arguments for the memory
            **kvargs: The keyword arguments for the LLM
        """
        super().__init__(system_message=system_message, **kvargs)
        if "system_prompt" in kvargs:
            del kvargs["system_prompt"]
        if llm is None:
            self.llm = FakeListLLM(**kvargs)
        else:
            self.llm = llm(**kvargs)
        if memory_kvargs is None:
            memory_kvargs = {}
        self.system_message = system_message
        if isinstance(self.llm, BaseChatModel):
            messages = []
            if system_message:
                messages.append(SystemMessage(content=system_message))
            messages.append(MessagesPlaceholder(variable_name="chat_history"))
            messages.append(HumanMessagePromptTemplate.from_template("{question}"))
            self.prompt = ChatPromptTemplate(messages=messages)
            self.memory = ConversationBufferWindowMemory(**memory_kvargs,
                                                         memory_key="chat_history",
                                                         return_messages=True)
        else:
            if system_message:
                s_message = f"System:{system_message}\n"
            else:
                s_message = ""
            template = s_message + """
{chat_history}
Human: {question}
AI:"""
            self.prompt = PromptTemplate(template=template,
                                         input_variables=["chat_history", "question"])
            self.memory = ConversationBufferWindowMemory(**memory_kvargs,
                                                         memory_key="chat_history")
        self.llm_chain = LLMChain(llm=self.llm,
                                  memory=self.memory,
                                  prompt=self.prompt)



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
            ai_response = self.llm_chain.predict(question=message, callbacks=[stream_handler])
        else:
            ai_response = self.llm_chain.predict(question=message)
        self.add_ai_message(message=ai_response)
        return ai_response


    def get_prompt_response_without_memory(self, message:str,
                                           stream_handler:Optional[BaseCallbackHandler]
                                           =None)->str:
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
            if isinstance(self.llm, BaseChatModel):
                return self.llm(callbacks=[stream_handler],
                                messages=[HumanMessage(content=message)]).content
            return self.llm(callbacks=[stream_handler], prompt=message)
        if isinstance(self.llm, BaseChatModel):
            return self.llm([HumanMessage(content=message)]).content
        return self.llm(prompt=message)
