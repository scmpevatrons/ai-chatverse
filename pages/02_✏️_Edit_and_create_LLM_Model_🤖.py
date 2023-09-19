"""
This page is used to edit and create LLM models
"""
import os
import streamlit as st
from models.meta_info import ModelMetaInfo
from conversations.conversation import Conversation
from app_utils import render_models_view,\
                      state_of_model,\
                      cancel_model_focus_mode,\
                      render_model_view, \
                      render_model_create, \
                      load_models, \
                      get_selected_model, \
                      is_model_locked, \
                      render_model_edit \
                        ,set_page_config


def delete_conversation(conversation:Conversation):
    """
    Delete the conversation
    Args:
        conversation (Conversation): The conversation to delete
    """
    conversations = st.session_state['conversations']
    index = 0
    while index < len(conversations):
        if conversations[index] == conversation:
            del conversations[index]
        else:
            index += 1
    if conversation == st.session_state['current_conversation']:
        st.session_state['current_conversation'] = None
    st.session_state['conversations'] = conversations


def delete_model(model_meta_info:ModelMetaInfo):
    """
    Delete the model
    Args:
        model_meta_info (ModelMetaInfo): The model meta info
        models (list[ModelMetaInfo]): The list of models
    """
    models = st.session_state['models']
    model_key_to_delete = None
    for model_key, meta_info in models.items():
        if meta_info == model_meta_info:
            model_key_to_delete = model_key
            for conversation in meta_info.get_conversations():
                delete_conversation(conversation)
    if model_key_to_delete:
        del models[model_key_to_delete]
    st.session_state['models'] = models
    cancel_model_focus_mode()



def render(config_file:str, app_home:str):
    """
    Render all the UI components for the app
    Args:
        config_file (str): The path to the config file
        app_home (str): The path to the app home directory
    """
    set_page_config()
    st.header("✏️ Edit and Create LLM Model 🤖")
    model_state = state_of_model()
    if model_state != "view":
        models = list(load_models(config_file, app_home).values())
        model_meta_info = get_selected_model(models)
        if model_state == "model_view":
            render_model_view(model_meta_info)
        elif model_state == "model_create":
            if not is_model_locked():

                model_meta = model_meta_info.get_serialised_model_data(view_mode=False,
                                                                       create_mode=True)
                st.session_state['model_meta_dict'] = model_meta
            render_model_create(models)
        elif model_state == "model_edit":
            if not is_model_locked():
                model_meta = model_meta_info.get_serialised_model_data(view_mode=False,
                                                                       create_mode=False)
                st.session_state['model_meta_dict'] = model_meta
            render_model_edit(model_meta_info)
        elif model_state == "model_delete":
            st.info("Are you sure you want to delete this model?")
            if model_meta_info.get_conversations():
                st.warning(("This model has conversations associated with it. "
                            "Deleting this model will delete all the conversations associated"
                            " with it."))
                for conversation in model_meta_info.get_conversations():
                    st.info(conversation.conversation_topic)
            lef_col, right_col = st.columns([10, 2])
            with lef_col:
                st.button("Cancel", key="cancel_model_focus_mode",
                        on_click=cancel_model_focus_mode)
            with right_col:
                st.button("🗑️", key="delete_model", on_click=delete_model, args=(model_meta_info,))
    else:
        render_models_view(config_file, app_home)


if __name__ == "__main__":
    DIR_NAME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CONFIG_FILE = os.path.join(DIR_NAME, "configs/config.yaml")
    render(CONFIG_FILE, DIR_NAME)
