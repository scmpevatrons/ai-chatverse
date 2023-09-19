"""
This file is used to render the page for Group chat view
"""
import os
from app_utils import render_group_agents_view, set_page_config

def render(config_file:str, dir_name:str):
    """
    This method is used to render the page for Group chat view
    
    Args:
        config_file: The path to the config file
        dir_name: The directory name
    """
    set_page_config()
    render_group_agents_view(config_file, dir_name)



if __name__ == "__main__":
    DIR_NAME = os.path.dirname(os.path.abspath(__file__))
    CONFIG_FILE = os.path.join(DIR_NAME, "configs/config.yaml")
    render(CONFIG_FILE, DIR_NAME)
