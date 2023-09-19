"""
This is the schema for a group message
"""
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class GroupMessage(BaseModel):
    """
    This is the class for a group message
    """
    sender_name: str = Field(description="The sender of the message")
    icon: str = Field(description="The icon of the sender")
    message: str = Field(description="The message")
    timestamp: datetime = Field(description="The timestamp of the message",
                                default_factory=datetime.now)
    message_type: Literal['AI', 'USER'] = Field(description="The type of the message")

