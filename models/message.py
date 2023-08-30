"""
This is the module for the message data class
"""
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class Message(BaseModel):
    """
    This is the class for a message
    """
    message:str = Field(description="The message")
    message_type: Literal['SYSTEM', 'USER', 'AI'] = Field(description="The type of message")
    timestamp: datetime = Field(description="The timestamp of the message",
                                default_factory=datetime.now)
