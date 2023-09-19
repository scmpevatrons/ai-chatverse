"""
This module has the necesary utils to deal with App Interface and intereactions
"""
import os
from datetime import datetime
from typing import Dict, Callable, List, Literal, Optional
from uuid import uuid4
from shutil import make_archive
import streamlit_nested_layout
import streamlit as st
from backend.backend import get_models, Conversation,\
                    ModelMetaInfo, start_conversation, \
                    summmarize_conversation, get_handler, \
                    get_group_agents
from ui_elements.format_option import FormatOption
from ui_elements.components import render_user_message, render_system_message, \
                                    render_group_ai_message, render_group_user_message
from conversations.group_conversation import GroupConversation
from schema.message import Message
from schema.group_message import GroupMessage
from schema.attachment_message import AttachmentMessage
from schema.group_agent import GroupAgent




def load_models(config_file:str, base_path:str)->Dict[str, ModelMetaInfo]:
    """
    This function loads the models from the config file
    If the models are already loaded, it returns the models from the session state
    
    Args:
        config_file: The path to the config file
        base_path: The base path of the app
    Returns:
       A dictionary of models with key as the model identifier and value as the model meta info object
    """
    if 'models' not in st.session_state:
        models = get_models(config_file, base_path)
        st.session_state['models'] = models
    else:
        models = st.session_state['models']
    return models

def load_group_agents(config_file:str, base_path:str)->Dict[str, GroupAgent]:
    """
    This function loads the group agents from the config file
    If the group agents are already loaded, it returns the group agents from the session state

    Args:
        config_file: The path to the config file
        base_path: The base path of the app
    Returns:
         A dictionary of group agents with key as the group agent identifier and value as the group agent object
    """
    if "group_agents" not in st.session_state:
        group_agents = get_group_agents(config_file, base_path)
        st.session_state["group_agents"] = group_agents
    return st.session_state["group_agents"]

def load_conversations()->List[Conversation]:
    """
    This function loads the conversations from the session state
    If the conversations are not loaded, it initializes the conversations
    
    Returns:
        The list of conversations
    """
    if 'conversations' not in st.session_state:
        st.session_state['conversations'] = []
        conversations = []
    else:
        conversations = st.session_state['conversations']
    return conversations


def set_current_conversation(conversation:Conversation)->None:
    """
    This function sets the current conversation to the session state
    
    Args:
        conversation: The conversation object to set as current conversation
    """
    st.session_state['current_conversation'] = conversation


def get_current_conversation()->Conversation:
    """
    This function returns the current conversation
    
    Returns:
        The current conversation
    """
    if 'current_conversation' not in st.session_state:
        current_conversation = None
        st.session_state['current_conversation'] = None
    else:
        current_conversation = st.session_state['current_conversation']
    return current_conversation


def reset_conversation()->None:
    """
    This function resets the screen to start a new conversation
    """
    st.session_state['current_conversation'] = None


def conversation_on_click(conversation:Conversation)->Callable[[], None]:
    """
    This function returns a function that is called when a conversation is clicked
    
    Args:
        conversation: The conversation object of the clicked conversation
    
    Returns:
        The function callback that is called when the conversation is clicked
    """
    def conversation_clicked_inner():
        st.session_state['current_conversation'] = conversation
    return conversation_clicked_inner


def render_sidebar(current_conversation:Conversation, all_conversations:List[Conversation])->None:
    """
    This function renders the sidebar with the list of conversations
    
    Args:
        current_conversation: The current conversation
        all_conversations: The list of all conversations
    """
    with st.sidebar:
        st.button("🧵 Start a new conversation", use_container_width=True,
                  on_click=reset_conversation)
        for i, conversation in enumerate(all_conversations):
            if not conversation.is_summarized:
                continue
            button_type = "primary" if conversation == current_conversation else "secondary"
            st.button(conversation.conversation_topic , use_container_width=True,
                      key=f"conversation_{i}",
                    type=button_type,
                    on_click=conversation_on_click(conversation))


def on_new_user_messaage(current_conversation:Conversation, model_used_by_user:ModelMetaInfo)->None:
    """
    This function is called when a new user message is submitted
    A new conversation is created if the current conversation doesnt exist
    
    Args:
        current_conversation: The current conversation
        model_used_by_user: The model used by the user
    """
    prompt = st.session_state.chat_input
    st.session_state['user_input'] = prompt
    if current_conversation is None:
        model_used_by_user.set_value_from_sidebar()
        conversation = start_conversation(prompt, model_used_by_user)
        st.session_state['conversations'].append(conversation)
    else:
        conversation = current_conversation
    set_current_conversation(conversation)


def render_conversation(current_conversation:Conversation, model_used_by_user:ModelMetaInfo)->None:
    """
    This function renders the conversation
    
    Args:
        current_conversation: The current conversation
        model_used_by_user: The model used by the user for the conversation
    """
    if current_conversation is None:
        return
    if hasattr(model_used_by_user, 'icon'):
        icon_path = model_used_by_user.icon
    else:
        icon_path = None
    messages = current_conversation.llm_model.get_messages()
    last_user_message = None
    for message in messages:
        if message.message_type == "USER":
            render_user_message(message)
            last_user_message = message
        else:
            render_system_message(message, last_user_message, icon_path=model_used_by_user.icon)
    if 'user_input' not in st.session_state:
        st.session_state['user_input'] = None
    user_input = st.session_state['user_input']
    if user_input:
        user_message = Message(message=user_input, message_type='USER', timestamp=datetime.now())
        render_user_message(user_message)
        system_message = Message(message="I am thinking...", message_type="AI")
        system_container, placeholder = render_system_message(system_message, user_message,
                                                              calculate_time=False,
                                                              icon_path=icon_path)
        with system_container:
            with st.spinner(":hourglass_flowing_sand:"):
                handler = get_handler(placeholder)
                system_response = current_conversation.llm_model.get_prompt_response(
                    user_message.message, handler)
                system_message.message = system_response
                system_message.timestamp = datetime.now()
            render_system_message(system_message, user_message, placeholder, system_container,
                                  icon_path=icon_path)
        if not current_conversation.is_summarized:
            with st.sidebar:
                container = st.empty()
                handler = get_handler(container)
                with st.spinner("Summarizing conversation..."):
                    sumarized_text = summmarize_conversation(current_conversation,
                                                             user_input, handler)
                container.empty()
                del container
                st.button(sumarized_text, use_container_width=True, type="primary",
                          on_click=conversation_on_click(current_conversation))
                current_conversation.conversation_topic = sumarized_text
                current_conversation.is_summarized = True
        st.session_state['user_input'] = None



def render_model_description(current_conversation:Conversation, \
                             model_used_by_user:ModelMetaInfo)->None:
    """
    This function renders the model description
    
    Args:
        current_conversation: The current conversation
        model_used_by_user: The model used by the user for the conversation
    """
    if hasattr(model_used_by_user, 'icon'):
        icon_path = model_used_by_user.icon
    else:
        icon_path = None
    _, model_icon_col,_ =  st.columns(3)
    if current_conversation is None:
        with model_icon_col:
            st.image(icon_path)
    st.info(model_used_by_user.description)


def is_model_locked()->bool:
    """
    This function returns whether the model is locked for edit/create
    
    Returns:
        True if the model is locked, False otherwise
    """
    if 'model_meta_dict' in st.session_state:
        return st.session_state['model_meta_dict'] is not None
    return False


def on_click_group_chat_in_focus(mode:Literal['agents_view', 'character_view', 'chat_view'],
                                 group_agent:GroupAgent)->Callable[[], None]:
    """
    This function returns a function that is called when a group agent is clicked
    
    Args:
        mode: The mode in which the group agent will be used
        group_agent: The group agent object
    
    Returns:
        The function callback that is to be called when the group agent is clicked
    """
    def group_chat_inner():
        st.session_state['view_mode'] = mode
        st.session_state['group_agent'] = group_agent
    return group_chat_inner


def get_group_view_mode()->Optional[Literal['agents_view', 'character_view', 'chat_view']]:
    """
    This function returns the group view mode
    """
    if 'view_mode' not in st.session_state:
        return 'agents_view'
    return st.session_state['view_mode']


def on_click_model_in_focus(mode:Literal['view', 'model_create', 'model_delete',
                                         'model_view', 'model_edit'],
                            model_meta_info:ModelMetaInfo)->Callable[[], None]:
    """
    This function returns a function that is called when a model is clicked
    
    Args:
        mode: The mode in which the model will be used
        model_meta_info: The model meta information
    
    Returns:
        The function callback that is to be called when the model is clicked
    """
    model_meta = None
    if model_meta_info:
        model_meta = model_meta_info.get_serialised_model_data(
                                                    view_mode=mode == 'model_view',
                                                    create_mode=mode == 'model_create')
    def edit_model_inner():
        st.session_state['model_meta_dict'] = model_meta
        st.session_state["chosen_model_name"] = model_meta_info.name if model_meta_info else None
        st.session_state['model_state'] = mode
    return edit_model_inner



def state_of_model()->Literal['view', 'model_create', 'model_delete',
                              'model_view', 'model_edit']:
    """
    This function returns the state of the model
    
    Returns:
        The state of the model
    """
    if 'model_state' not in st.session_state:
        st.session_state['model_state'] = 'view'
    return st.session_state['model_state']


def get_model_in_focus()->dict[str, FormatOption]:
    """
    This function returns the model meta information of the model in focus
    
    Returns:
        The model meta information of the model in focus
    """
    return st.session_state['model_meta_dict']


def cancel_model_focus_mode()->None:
    """
    This function cancels the edit mode
    """
    st.session_state['model_state'] = 'view'
    st.session_state['model_meta_dict'] = None


FIELD_TYPES = ["STRING", "INT", "FLOAT",
               "BOOL", "LIST", "DICT",
               "SECRET_STRING", "LONG_STRING",
               "IMAGE_PATH"]



def render_model_view(model_meta_info:ModelMetaInfo)->None:
    """
    This function renders the model view
    
    Args:
        model_meta_info: The model meta information
    """
    st.button("◀️ Back", key="back", on_click=cancel_model_focus_mode)
    model_dict = st.session_state['model_meta_dict']
    model_meta_info.render_model_in_view_mode(model_dict)


def on_base_model_change(key:str, model_meta_infos:List[ModelMetaInfo]):
    """
    This function is called when the base model is changed
    
    Args:
        key: The key of the selectbox
        model_meta_infos: The list of model meta information
    """
    selected_name = st.session_state[key]
    st.session_state['chosen_model_name'] = selected_name
    selected_model = get_selected_model(model_meta_infos)
    st.session_state['model_meta_dict'] = selected_model.get_serialised_model_data(
        create_mode=True
    )


def get_selected_model(model_meta_infos:List[ModelMetaInfo])->Optional[ModelMetaInfo]:
    """
    This function returns the selected model
    
    Args:
        model_meta_infos: The list of model meta information objects
    Returns:
        The selected model
    """
    if 'chosen_model_name' not in st.session_state or \
        st.session_state['chosen_model_name'] is None:
        return model_meta_infos[0]
    chosen_model = [model for model in model_meta_infos 
                    if model.name == st.session_state['chosen_model_name']]
    if chosen_model:
        return chosen_model[0]


def add_model(model_meta_info:ModelMetaInfo)->None:
    """
    This function adds a model
    
    Args:
        model_meta_info: The model meta information
    """
    new_model_key = str(len(st.session_state['models'])) + "_" + model_meta_info.name
    model_meta_info.is_persistent = False
    model_meta_info.key = new_model_key
    st.session_state['models'][new_model_key] = model_meta_info


def model_exists(models:list[ModelMetaInfo], name:str, ignore:Optional[ModelMetaInfo]=None)->bool:
    """
    This function checks if the model exists with the given name
    
    Args:
        models: The list of models
        name: The name of the model
        ignore: The model to ignore (used in edit mode)
    Returns:
        True if the model exists, False otherwise
    """
    for model in models:
        if model == ignore:
            continue
        if model.name == name:
            return True
    return False


def create_model(model_meta_info:ModelMetaInfo)->None:
    """
    This function creates a model
    
    Args:
        model_meta_info: The model meta information
    """
    model_meta_dict = st.session_state['model_meta_dict']
    model_meta_dict = model_meta_info.get_data_from_meta(model_meta_dict)
    models = list(st.session_state['models'].values())
    name = model_meta_info.get_value(model_meta_dict['name'])
    if model_exists(models, name):
        st.toast(f"Model with name {name} already exists", icon="⚠️")
        return
    selected_model = get_selected_model(models)
    for key, value in selected_model.model_dump().items():
        if key not in model_meta_dict:
            model_meta_dict[key] = value
    model_meta_info = model_meta_info.__class__.create_model(model_meta_dict)
    if model_meta_info is None:
        return
    add_model(model_meta_info)
    st.session_state['model_state'] = 'view'
    st.session_state['model_meta_dict'] = None


def edit_model(model_meta_info:ModelMetaInfo)->None:
    """
    This function edits a model
    
    Args:
        model_meta_info: The model meta information
    """
    model_meta_dict = st.session_state['model_meta_dict']
    model_meta_dict = model_meta_info.get_data_from_meta(model_meta_dict)
    models = list(st.session_state['models'].values())
    name = model_meta_info.get_value(model_meta_dict['name'])
    if model_exists(models, name, ignore=model_meta_info):
        st.toast(f"Model with name {name} already exists", icon="⚠️")
        return
    valid_edit = model_meta_info.validate_edit_and_save_state(model_meta_dict)
    if not valid_edit:
        return
    st.session_state['model_state'] = 'view'
    st.session_state['model_meta_dict'] = None


def render_model_edit(model_meta_info:ModelMetaInfo)->None:
    """
    This function renders the model create view
    
    Args:
        model_meta_info: The model meta information
    """
    st.button("◀️ Back", key="back", on_click=cancel_model_focus_mode)
    model_dict = st.session_state['model_meta_dict']
    model_meta_info.render_model_in_edit_mode(model_dict)
    cols = st.columns([10, 3])
    with cols[1]:
        st.button("Edit and Save", key="edit", on_click=edit_model, args=(model_meta_info, ),
                  type="primary")


def get_current_model_index(models:List[ModelMetaInfo], chosen_model_name:str)->int:
    """
    This function returns the index for the user chosen model
    
    Args:
        models: The list of models
        chosen_model_name: The current model
    
    Returns:
        The current model index
    """
    for key, model in enumerate(models):
        if model.name == chosen_model_name:
            return key
    return 0


def render_model_create(model_meta_infos:List[ModelMetaInfo])->None:
    """
    This function renders the model create view
    
    Args:
        model_meta_info: The model meta information
    """
    st.button("◀️ Back", key="back", on_click=cancel_model_focus_mode)
    key = "inherit_from"
    model_dict = st.session_state['model_meta_dict']
    chosen_model_name = st.session_state.get('chosen_model_name')
    model_index = get_current_model_index(model_meta_infos, chosen_model_name)
    chosen_model_meta = model_meta_infos[model_index]
    st.selectbox("Inherit From", [model.name for model in model_meta_infos],
                 key=key, on_change=on_base_model_change, args=(key, model_meta_infos),
                 index=model_index)
    st.info("We support creating session models from available models for now")
    chosen_model_meta.__class__.render_model_in_create_mode(model_dict)
    cols = st.columns([10, 2])
    with cols[1]:
        st.button("Create", key="create", on_click=create_model,
                  args=(chosen_model_meta,),
                  type="primary")



def validate_settings_and_start_group_chat(group_agent:GroupAgent)->None:
    """
    This function validates the settings and starts the group chat
    
    Args:
        group_agent: The group agent object
    """
    group_meta_dict = st.session_state['group_meta_dict']
    group_meta_dict = group_agent.setting.get_data_from_meta(group_meta_dict)
    open_ai_api_key = group_agent.setting.get_value(group_meta_dict['openai_api_key'])
    if len(open_ai_api_key) <= 30:
        st.toast("Please enter a valid openai api key", icon="⚠️")
        return
    if group_agent.setting.validate_edit_and_save_state(group_meta_dict):
        st.session_state['view_mode'] = 'chat_view'


def get_group_conversations()->List[GroupConversation]:
    """
    This function returns the group conversations
    
    Returns:
        The list of group conversations
    """
    if 'group_conversations' not in st.session_state:
        st.session_state['group_conversations'] = []
    return st.session_state['group_conversations']

def get_current_group_conversation()->Optional[GroupConversation]:
    """
    This function returns the current group conversation
    
    Returns:
        The current group conversation
    """
    if 'current_group_conversation' not in st.session_state:
        st.session_state['current_group_conversation'] = None
    return st.session_state['current_group_conversation']


def group_chat_on_submit(key:str, group_agent:GroupAgent)->None:
    idea = st.session_state[key]
    st.session_state["current_idea"] = idea
    group_conversation = GroupConversation(group_agent=group_agent, conversation_topic=idea)
    user_character = group_agent.get_character('user')
    user_message = GroupMessage(sender_name=user_character.name,
                                icon=user_character.icon,
                                message=idea,
                                message_type='USER')
    group_conversation.add_message(user_message)
    st.session_state['current_group_conversation'] = group_conversation
    group_conversations = get_group_conversations()
    group_conversations.append(group_conversation)




def render_group_conversation(group_conversation:GroupConversation)->None:
    """
    This function renders the group conversation
    
    Args:
        group_conversation: The group conversation object
    """
    messages = group_conversation.messages
    for message in messages:
        if message.message_type.upper() == "USER":
            render_group_user_message(message)
        else:
            render_group_ai_message(message, show_time=True)


def group_conversation_on_click(group_conversation:GroupConversation)->None:
    """
    This function is called when a group conversation is clicked
    
    Args:
        group_conversation: The group conversation object
    """
    st.session_state['view_mode'] = 'chat_view'
    st.session_state['current_group_conversation'] = group_conversation


def reset_group_conversation()->None:
    """
    This function resets the group conversation
    """
    st.session_state['view_mode'] = 'agents_view'


def render_group_agents_view(config_file:str, base_path:str)->None:
    """
    This function renders the group agents view

    Args:
        config_file: The path to the config file
        base_path: The base path
    """
    group_conversations = get_group_conversations()
    current_conversation = get_current_group_conversation()
    with st.sidebar:
        st.button("🧵 Start a new conversation", use_container_width=True,
                  on_click=reset_group_conversation)
        for group_conversation in group_conversations:
            st.button(group_conversation.conversation_topic, use_container_width=True,
                        on_click=group_conversation_on_click,
                        type="primary" if group_conversation == current_conversation else "secondary",
                        args=(group_conversation,),
                        key=group_conversation.conversation_topic)
        
    if get_group_view_mode() == 'agents_view':
        st.info("This is the page where you start a group conversation")
        group_agents = load_group_agents(config_file, base_path)
        for group_agent_name, group_agent in group_agents.items():
            pic, meta_info, button_section = st.columns([2, 6, 2])
            with pic:
                st.image(group_agent.icon, width=100)
            with meta_info:
                st.subheader(group_agent.name)
                st.write(group_agent.description)
                st.image(group_agent.flow_diagram)
            with button_section:
                st.button("Start Chat", type="primary", key=f"{group_agent_name}_view",
                        on_click=on_click_group_chat_in_focus('character_view', group_agent))
    else:
        view_mode = get_group_view_mode()
        group_agent:GroupAgent = st.session_state['group_agent']
        if view_mode == 'character_view':
            st.button("◀️ Back", key="back", on_click=reset_group_conversation)
            st.info(group_agent.description)
            st.image(group_agent.flow_diagram)
            st.subheader("Group Chat Characters")
            num_characters_in_a_row = 3
            i = 0
            while i < len(group_agent.characters):
                if i % num_characters_in_a_row == 0:
                    cols = st.columns(num_characters_in_a_row)
                character = group_agent.characters[i]
                with cols[i % num_characters_in_a_row]:
                    icon_col, meta_info_col = st.columns([3, 6])
                    with icon_col:
                        st.image(character.icon, width=75)
                    with meta_info_col:
                        st.subheader(character.name)
                        st.write(character.description)
                i += 1
            st.subheader("Settings")
            st.session_state['group_meta_dict'] = group_agent.setting.get_serialised_model_data()
            group_agent.setting.render_model_in_edit_mode(st.session_state['group_meta_dict'])

            cols = st.columns([10, 2])
            with cols[1]:
                st.button("Start Chat", type="primary", key=f"{group_agent.name}_start_view",
                        on_click=validate_settings_and_start_group_chat, args=(group_agent,))
        else:
            key = "group_chat_input"
            if current_conversation is None:
                st.chat_input("Enter your message here", key=key, on_submit=group_chat_on_submit, args=(key, group_agent,))
                st.subheader("Chat with " + group_agent.name)
                st.write(group_agent.usage_description)
                st.header("Examples")
                for example in group_agent.examples:
                    st.subheader(example.name)
                    st.info(example.description)
            group_conversation = get_current_group_conversation()
            if group_conversation is not None:
                render_group_conversation(group_conversation)
                if len(group_conversation.get_messages()) == 1:
                    group_conversation.group_agent.run(group_conversation.conversation_topic)
                    artifact_basename = os.path.basename(group_conversation.final_artifact)
                    group_conversation.done = True
                    session_id = get_session_id()
                    archive_name = f"artifacts/{session_id}_{artifact_basename}"
                    artifact_file = make_archive(archive_name, 'zip', group_conversation.final_artifact)
                    message = AttachmentMessage(sender_name=group_agent.name, icon=group_agent.icon,
                                                message=artifact_file, message_type="AI",
                                                attachment_type="Final Artifact")
                    group_conversation.add_message(message)
                    render_group_ai_message(message, show_time=True)


def get_session_id()->str:
    """
    This function returns the session id
    """
    if 'session_id' not in st.session_state:
        st.session_state['session_id'] = str(uuid4())
    return st.session_state['session_id']



def render_models_view(config_file:str, base_path:str)->None:
    """
    This function renders the models view
    
    Args:
        config_file: The path to the config file
        base_path: The base path
    """
    st.info("This is the page where you can edit or create a session model")

    session_tab, persistent_tab = st.tabs(["Session Models", "Persistent Model"])
    models = load_models(config_file, base_path)
    persistent_models = {key: model for key, model in models.items() if model.is_persistent}
    session_models = {key: model for key, model in models.items() if not model.is_persistent}


    with persistent_tab:
        for model_key, model_meta_info in persistent_models.items():
            pic, meta_info, view_button = st.columns([2, 6, 1])
            with pic:
                st.image(model_meta_info.icon, width=100)
            with meta_info:
                st.subheader(model_meta_info.name)
                st.write(model_meta_info.description)
            with view_button:
                st.button("View", key=model_key,
                          on_click=on_click_model_in_focus('model_view', model_meta_info))

    with session_tab:
        if len(session_models) == 0:
            st.warning("No session models available")
        st.button("Create New Model", key="create_new_model",
                  on_click=on_click_model_in_focus('model_create', None))
        for model_key, model_meta_info in session_models.items():
            pic, meta_info, button_section = st.columns([2, 6, 1])
            with pic:
                st.image(model_meta_info.icon, width=100)
            with meta_info:
                st.subheader(model_meta_info.name)
                st.write(model_meta_info.description)
            with button_section:
                st.button("👁️", key=f"{model_key}_view",
                          on_click=on_click_model_in_focus('model_view', model_meta_info))
                st.button("✏️", key=f"{model_key}_edit",
                          on_click=on_click_model_in_focus('model_edit', model_meta_info))
                st.button("🗑️", key=f"{model_key}_delete",
                          on_click=on_click_model_in_focus('model_delete', model_meta_info))
                

def set_page_config():
    """
    This function sets the page config for Streamlit app
    """
    about = """
    # :robot_face: AI ChatVerse
    This is an Opensource App for playing with Language Models

    Created by [pevatrons](https://www.pevatrons.net)
    """
    st.set_page_config(page_title="AI ChatVerse", page_icon=":robot_face:", menu_items={
        'About': about
    })
