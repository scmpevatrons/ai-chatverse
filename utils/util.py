"""
The util module contains all the utility functions
"""
from typing import Any, Dict, Optional

class InvalidConfigError(Exception):
    """
    This exception is raised when the config file is invalid
    """


def clear_default_values(dict_model:Dict[str, Any])->Dict[str, Any]:
    """
    Clears the default values from the model
    
    Args:
        dict_model: The model
    
    Returns:
        The model without default values
    """
    default_values = {"icon" : "llm_model.png"}
    for key, value in dict_model.copy().items():
        if isinstance(value, (list, dict)):
            continue
        if value is None:
            del dict_model[key]
        if key in default_values and default_values[key] == value:
            del dict_model[key]
    return dict_model

def get_field_name(data:dict[str, Any], field_names:list[str])->Optional[str]:
    """
    Gets the field name from the data
    
    Args:
        data: The data to verify the field name.
        field_names: The field names to check for
    Returns:
        The field name if found else None
    """
    for field_name in field_names:
        if field_name in data:
            return field_name
    return None

