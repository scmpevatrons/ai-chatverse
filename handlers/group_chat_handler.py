"""
This file contains the class used to handle the callback from MetaGPT to Streamlit
"""
import os
import streamlit as st
from metagpt.callbacks import BaseCallbackHandler, SenderInfo
from ui_elements.components import render_group_ai_message
from schema.group_message import GroupMessage
from schema.attachment_message import AttachmentMessage


class StreamlitCallbackHandler(BaseCallbackHandler):
    """
    This class is used to handle the callback from MetaGPT to Streamlit
    """

    def __init__(self, profile_pic:str, investment:float, cost_container):
        """
        This method is used to initialize the class

        Args:
            profile_pic: The path to the profile pic
            investment: The investment
            cost_container: The cost container
        """
        self.investement = investment
        self.group_conversation = st.session_state['current_group_conversation']
        self.group_message = None
        self.profile_pic = profile_pic
        self.container = None
        self.text = ""
        self.sender_info = None
        self.sender_string = None
        self.messages_to_be_rendered = []
        self.investement = investment
        self.cost_container = cost_container
        self.placeholder = None


    def on_new_workspace_generated(self, workspace_path: str) -> None:
        """
        This method is used to handle the new workspace generated event

        Args:
            workspace_path: The workspace path
        """
        self.group_conversation.final_artifact = workspace_path


    def on_new_message(self, sender_info: SenderInfo) -> None:
        """
        This method is used to handle the new message event

        Args:
            sender_info: The sender info object
        """
        self.sender_info = sender_info
        self.sender_string = f"{sender_info.name} - {sender_info.role}"
        self.group_message = GroupMessage(sender_name=self.sender_string,
                                          icon=self.profile_pic,
                                          message="",
                                          message_type="AI")
        container, placeholder = render_group_ai_message(self.group_message, None, None)
        self.container = container
        self.placeholder = placeholder
        self.text = ""

    def on_new_token_generated(self, token: str) -> None:
        """
        This method is used to handle the new token generated event

        Args:
            token: The token
        """
        self.text += token
        self.group_message.message = self.text +"▌"
        with self.placeholder.container():
            st.subheader(self.group_message.sender_name)
            st.markdown(self.group_message.message)


    def on_message_end(self) -> None:
        """
        This method is used to handle the message end event
        """
        self.group_message.message = self.text
        render_group_ai_message(self.group_message, self.container, self.placeholder, show_time=True)
        self.group_conversation.add_message(self.group_message)
        self.group_message = None
        for message in self.messages_to_be_rendered:
            render_group_ai_message(message, show_time=True)


    def on_new_file_generated(self, sender_info: SenderInfo, file_type: str, file_path: str) -> None:
        """
        This method is used to handle the new file generated event

        Args:
            sender_info: The sender info object
            file_type: The file type
            file_path: The file path
        """
        if os.path.exists(file_path):
            extension = file_path.split(".")[-1]
            if extension not in ['jpg', 'png', 'jpeg']:
                return
            sender_string = f"{sender_info.name} - {sender_info.role}"
            attachment_message = AttachmentMessage(sender_name=sender_string,
                                                   icon=self.profile_pic,
                                                   message=file_path,
                                                   message_type="AI",
                                                   attachment_type=file_type)
            self.group_conversation.add_message(attachment_message)
            if self.group_message is not None:
                self.messages_to_be_rendered.append(attachment_message)
            else:
                render_group_ai_message(attachment_message)

    def on_cost_updated(self, cost: float) -> None:
        """
        This method is used to handle the cost updated event

        Args:
            cost: The cost
        """
        self.cost_container.empty()
        with self.cost_container.container():
            progress = min(1.0, (cost / self.investement))
            st.progress(progress, text=f"Cost: {cost:.2f}$ / {self.investement} $")
