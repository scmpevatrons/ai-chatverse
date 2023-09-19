from typing import Optional
from pydantic import BaseModel, Field
from schema.group_message import GroupMessage
from schema.group_agent import GroupAgent


class GroupConversation(BaseModel):
    """
    This class is used to store the group conversation
    """
    conversation_topic:Optional[str] = Field(description="The conversation topic", default=None)
    messages: list[GroupMessage] = Field(description="The messages in the conversation", default_factory=list)
    group_agent:GroupAgent = Field(description="The group agent")
    final_artifact:str = Field(description="The final artifact", default=None)
    done : bool = Field(validation_alias="Done", description="The done flag", default=False)

    
    class Config:
        """
        This class is used to configure the pydantic model
        """
        arbitrary_types_allowed = True


    def add_message(self, message:GroupMessage)->None:
        """
        Adds a message to the conversation

        Args:
            message: The message to add
        """
        self.messages.append(message)

    def get_messages(self)->list[GroupMessage]:
        """
        Gets the messages

        Returns:
            The messages
        """
        return self.messages