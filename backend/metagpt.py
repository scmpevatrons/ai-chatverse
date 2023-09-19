import asyncio
import streamlit as st
from metagpt.roles import Architect, Engineer, ProductManager
from metagpt.roles import ProjectManager, QaEngineer
from metagpt.software_company import SoftwareCompany
from metagpt.config import CONFIG
from handlers.group_chat_handler import StreamlitCallbackHandler
from ui_elements.group_setting import MetaGPTSetting




def run_metagpt(setting:MetaGPTSetting, characters:list['GroupAgentCharacter'],
                idea:str):
    with st.sidebar:
        cost_container = st.empty()
        cost_container.progress(0)
    mapping = {Architect : 'Architect',
               Engineer : 'Engineer',
               ProductManager : 'Product Manager',
               ProjectManager : 'Project Manager',
               QaEngineer : 'QA Engineer'}
    character_role_map = {}
    for character in characters:
        character_role_map[character.role] = character

    company = SoftwareCompany()
    roles_to_hire = [ProductManager, Architect, ProjectManager]
    CONFIG.openai_api_key = setting.openai_api_key
    # if implement or code_review
    if setting.implement or setting.code_review:
        # developing features: implement the idea
        roles_to_hire.append(Engineer)

    if setting.run_tests:
        # developing features: run tests on the spot and identify bugs
        # (bug fixing capability comes soon!)
        roles_to_hire.append(QaEngineer)

    role_objs_to_hire = []
    for role in roles_to_hire:
        role_name = mapping[role]
        character = character_role_map[role_name]
        options = {"name" : character.name, 
                   "callback_handler" : StreamlitCallbackHandler(character.icon,
                                                                 setting.investment,
                                                                 cost_container)
                   }
        if mapping[role] == 'Engineer':
            options["use_code_review"] = setting.code_review
            options["n_borg"] = 5
        role_obj = role(**options)
        role_objs_to_hire.append(role_obj)
    
    company.hire(role_objs_to_hire)
    company.invest(setting.investment)
    company.start_project(idea)
    asyncio.run(company.run(n_round=5))
