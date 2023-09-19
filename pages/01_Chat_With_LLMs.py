"""
This module is the streamlit app for the AI ChatVerse
"""
import os
import streamlit as st
from app_utils import load_models, on_new_user_messaage, \
                      get_current_conversation, load_conversations, \
                      render_conversation, \
                      render_sidebar, render_model_description, \
                      set_page_config



def render(config_file:str, app_home:str):
    """
    Render all the UI components for the app
    Args:
        config_file (str): The path to the config file
        app_home (str): The path to the app home directory
    """
    # Set the APP name and the favicon
    set_page_config()
    models = load_models(config_file, app_home)
    # Have all the model names for the select box
    model_names = []
    name_key_reverse_map = {}
    for key, model in models.items():
        model_names.append(model.name)
        name_key_reverse_map[model.name] = key
    current_conversation = get_current_conversation()
    all_conversations = load_conversations()
    model = st.selectbox("Select Model", model_names, 
                     disabled=current_conversation is not None,
                     index=model_names.index(models[current_conversation.key].name) \
                        if current_conversation else 0)
    model_used_by_user = models[name_key_reverse_map[model]]
    render_model_description(current_conversation, model_used_by_user)
    model_used_by_user.render_sidebar()
    render_sidebar(current_conversation, all_conversations)
    st.chat_input("Ask something to " + model, key="chat_input",
                  kwargs={"current_conversation" : current_conversation,
                          "model_used_by_user" : model_used_by_user},
                  on_submit=on_new_user_messaage)
    render_conversation(current_conversation, model_used_by_user)



if __name__ == "__main__":
    # Render everything
    # Load the models from the config file to the session

    DIR_NAME = os.path.dirname(os.path.dirname(__file__))
    CONFIG_FILE = os.path.join(DIR_NAME, "configs/config.yaml")
    render(CONFIG_FILE, DIR_NAME)
