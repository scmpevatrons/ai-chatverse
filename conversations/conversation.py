"""
This module contains the Conversation class
"""
from typing import Optional
from pydantic import BaseModel, Field
from models.base_model import BaseLLMModel


class Conversation(BaseModel):
    """
    This class is used to store the information for a conversation
    """
    conversation_topic:str = Field(description="The conversation topic")
    key: str = Field(description="The key of the model")
    llm_model: BaseLLMModel = Field(description="The model used in the conversation")
    is_summarized: Optional[bool] = Field(
                                    description="Whether the conversation is summarized or not",
                                    default=False)


    class Config:
        """
        This class is used to configure the pydantic model
        """
        arbitrary_types_allowed = True
