"""
This is the module for the attachment message
"""
import os
from pydantic import Field, field_validator
from schema.group_message import GroupMessage

class AttachmentMessage(GroupMessage):
    """
    This is the class for an attachment message
    """
    
    attachment_type: str = Field(description="The type of the attachment")


    @field_validator('message')
    @classmethod
    def validate_attachment_message(cls, value):
        """
        This method is used to validate the attachment message

        Args:
            value: The value of the message

        Returns:
            The value of the message
        """
        if not os.path.exists(value):
            raise ValueError(f"File {value} does not exist")
        return value
