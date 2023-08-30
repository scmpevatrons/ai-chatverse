"""
The util module contains all the utility functions
"""
import yaml
from backend.config_file import ConfigFile

class InvalidConfigError(Exception):
    """
    This exception is raised when the config file is invalid
    """



def pydantic_validate_config(config_file:str, base_path:str)->ConfigFile:
    """
    Validates the config file using pydantic
    Args:
        config_file: The path to the config file
        base_path: The base path of the app
    Returns:
        The validated config file
    """
    with open(config_file, encoding="utf-8") as file_handler:
        try:
            config = yaml.safe_load(file_handler)
        except yaml.YAMLError as exc:
            raise exc
    return ConfigFile(base_dir=base_path, **config)
