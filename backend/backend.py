"""
This file contains the backend logic for the streamlit app
"""
import sys
import os
from importlib.util import spec_from_file_location, module_from_spec
from typing import Dict
from langchain import PromptTemplate
from schema.config import pydantic_validate_config
from schema.group_agent import GroupAgent
from models.meta_info import ModelMetaInfo
from models.base_langchain_model import StreamlitDisplayHandler
from conversations.conversation import Conversation


def get_group_agents(config_file:str, base_path:str)->dict[str, GroupAgent]:
    """
    This method is used to get the group agents from the config file
    
    Args:
        config_file: The path to the config file
        base_path: The base path to the config file
    
    Returns:
        The group agents in the config file
    """
    group_agents = pydantic_validate_config(config_file, base_path).group_chat_agents
    group_agent_objects = {}
    for group_agent_name, group_agent in group_agents.items():
        group_agent_objects[group_agent_name] = group_agent
    return group_agent_objects


def get_models(config_file:str, base_path:str)->Dict[str, ModelMetaInfo]:
    """
    This method is used to get the models from the config file
    
    Args:
        config_file: The path to the config file
        base_path: The base path to the config file
    
    Returns:
        The models in the config file
    """
    models = pydantic_validate_config(config_file, base_path).models
    model_objects = {}
    for model_name, model_meta_info in models.items():
        model_objects[model_name] = model_meta_info
    return model_objects


def start_conversation(conversation_topic:str, model_meta_info:ModelMetaInfo)->Conversation:
    """
    This method is used to start a conversation
    
    Args:
        conversation_topic: The conversation topic
        model_meta_info: The model meta information
    
    Returns:
        The conversation object
    """
    model_file_name = os.path.basename(model_meta_info.llm_model_file)
    abs_module_file = model_meta_info.llm_model_file
    model_class = model_meta_info.llm_model_class
    module_name = model_file_name.split('.', 1)[0]
    spec = spec_from_file_location(module_name, abs_module_file)
    module = module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    model_class = getattr(module, model_class)
    system_message = model_meta_info.system_message
    kvargs = model_meta_info.llm_arguments
    memory_kvargs = model_meta_info.memory_arguments
    model_object = model_class(system_message=system_message, memory_kvargs=memory_kvargs, **kvargs)
    new_conversation = Conversation(conversation_topic=conversation_topic,
                        key=model_meta_info.key,
                        llm_model=model_object)
    model_meta_info.add_conversation(new_conversation)
    return new_conversation



def summmarize_conversation(conversation: Conversation,
                            content_to_summarize:str,
                            handler:StreamlitDisplayHandler)->str:
    """
    This method is used to summarize a conversation
    
    Args:
        conversation: The conversation object
        content_to_summarize: The content to summarize
        handler: The streamlit display handler
    
    Returns:
        The summary onf the conversation
    """
    message = ['Human: Summarize """Hello world""" to less than 5 words',
    'AI: Hello World',
    'Summarize: """{content}""" to less than 5 words',
    'AI:']
    flow = "\n".join(message)
    summarization_prompt = PromptTemplate(
        input_variables=["content"],
        template=flow
    )

    return conversation.llm_model.get_prompt_response_without_memory(
        summarization_prompt.format(content=content_to_summarize),
        stream_handler=handler)


def get_handler(container)->StreamlitDisplayHandler:
    """
    This method is used to get the handler to deal with streaming data
    
    Args:
        container: The streamlit container
    Returns:
        The streamlit display handler
    """
    return StreamlitDisplayHandler(container)
