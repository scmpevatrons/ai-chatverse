"""
This file contains the functions to render the user and system messages
"""
import os
import streamlit as st
from schema.message import Message
from schema.group_message import GroupMessage
from schema.attachment_message import AttachmentMessage


def render_user_message(message:Message)->None:
    """
    This function renders the user message
    
    Args:
        message: The message object containing user message
    """
    columns_weights = [0.5, 0.5]
    _, user_col = st.columns(columns_weights)
    with user_col:
        with st.chat_message("user"):
            st.write(message.message)
        st.write(message.timestamp.strftime("%I:%M %p"))


def render_system_message(message:Message, previous_user_message:Message,
                          message_placeholder=None, container=None,
                          calculate_time=True, icon_path=None)->tuple[st.container, st.empty]:
    """
    This function renders the system message
    
    Args:
        message: The message object containing system message
        previous_user_message: The previous user message
        message_placeholder: The placeholder to write the message
        container: The container of the system message.
        calculate_time: Whether to calculate the time taken for the system to respond
        icon_path: The path to Model chat Icon
    
    Returns:
        The container and the message placeholder of the system message
    """
    columns_weights = [0.9, 0.1]
    system_col, _ = st.columns(columns_weights)
    with system_col:
        if container is None:
            container = st.chat_message("assistant", avatar=icon_path)
        else:
            container.empty()
        with container:
            if message_placeholder:
                message_placeholder.write(message.message)
            else:
                message_placeholder = st.empty()
                message_placeholder.write(message.message)
    if calculate_time:
        # columns to store the time taken for the system to respond
        system_time_col, _ = st.columns([0.3, 0.7])
        time_taken_for_response = message.timestamp - previous_user_message.timestamp
        time_in_ms = time_taken_for_response.total_seconds()
        with system_time_col:
            st.write(f"🕓 {time_in_ms:0.2f}s " + message.timestamp.strftime("%I:%M %p"))
    return container, message_placeholder


def render_group_user_message(message:GroupMessage)->None:
    """
    This function renders the group user message

    Args:
        message: The message object containing user message
    """
    column_weights = [0.5, 0.5]
    _, user_col = st.columns(column_weights)
    with user_col:
        with st.chat_message(message.sender_name, avatar=message.icon):
            st.subheader(message.sender_name)
            st.write(message.message)
            system_time_col, _ = st.columns([0.3, 0.7])
            with system_time_col:
                st.write(message.timestamp.strftime("%I:%M %p"))


    
def render_group_ai_message(message:GroupMessage, container=None,
                            placeholder=None, show_time=False)->None:
    """
    This function renders the group system message

    Args:
        message: The message object containing system message
        container: The container of the system message.
        placeholder: The placeholder to write the message
        show_time: Whether to show the time
    """
    column_weights = [0.9, 0.1]
    system_col, _ = st.columns(column_weights)
    with system_col:
        if container is None:
            container = st.chat_message("assistant", avatar=message.icon)
            with container:
                placeholder = st.empty()
        else:
            placeholder.empty()
        with placeholder.container():
            st.subheader(message.sender_name)
            if type(message) == AttachmentMessage:
                if message.message.split(".")[-1] in ['jpg', 'png', 'jpeg']:
                    st.image(message.message, caption=message.attachment_type)
                else:
                    file_name = os.path.basename(message.message)
                    with open(message.message, 'rb') as fh:
                        st.download_button(f"Download {message.attachment_type}",
                                            fh, file_name)
            else:
                st.write(message.message)
            if show_time:
                system_time_col, _ = st.columns([0.2, 0.8])
                with system_time_col:
                    st.write(message.timestamp.strftime("%I:%M %p"))
    return container, placeholder
