"""
This module is used to define the config file schema
"""
from typing import Any, Dict
import yaml
from pydantic import BaseModel, Field, model_validator, field_validator
from models.meta_info import ModelMetaInfo
from schema.group_agent import GroupAgent
from schema.shared_state import get_shared_state
from utils.util import clear_default_values, get_field_name


class ConfigFile(BaseModel):
    """
    This class is used to store the information for the config file
    """

    models:Dict[str, ModelMetaInfo] = Field(validation_alias="Models", description="The models")
    keys:set[str] = Field(validation_alias="Keys", description="The model keys",
                          default_factory=set)
    base_dir:str = Field(validation_alias="BaseDir", description="The base directory", default=None)
    group_chat_agents:Dict[str, GroupAgent] = Field(validation_alias="GroupChatAgents",
                                                    description="The group chat agents")
    shared_state:Dict[str, Any] = Field(validation_alias="SharedState",
                                        description="The shared state", default_factory=dict)


    @field_validator("shared_state")
    @classmethod
    def validate_shared_state(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        This method is used to validate the shared state
        
        Args:
            data: The data
        
        Returns:
            The data
        """
        SHARED_CONFIG = get_shared_state()
        SHARED_CONFIG.update(**data)
        return data


    @model_validator(mode='before')
    @classmethod
    def validate_models_and_add_base_dir(cls, data: Any) -> Any:
        """
        This method is used to validate the models
        
        Args:
            data: The data
        
        Returns:
            The data
        """
        if isinstance(data, dict):
            model_key = get_field_name(data, ["models", "Models"])
            if model_key is None:
                raise ValueError("Models key not found in config file")
            models = data[model_key]
            for model_key, model in models.items():
                if "base_dir" not in model:
                    model["base_dir"] = data["base_dir"]
            group_chat_agents_key = get_field_name(data, ["group_chat_agents", "GroupChatAgents"])
            if group_chat_agents_key is None:
                raise ValueError("GroupChatAgents key not found in config file")
            group_chat_agents = data[group_chat_agents_key]
            for group_chat_agent in group_chat_agents.values():
                group_chat_agent["base_dir"] = data["base_dir"]
        return data


    @model_validator(mode="after")
    def after_models_validate(self)-> 'ConfigFile':
        """
        This method is used to validate the models
        
        Returns:
            The config file object
        
        Raises:
            InvalidConfigError: If the models are invalid
        """
        models_already_validated = {}
        for model_key, model in self.models.items():
            if model_key in self.keys:
                raise ValueError(f"Model key {model_key} already exists")
            self.keys.add(model_key)
            model.key = model_key
            if model.inherits_from is None:
                models_already_validated[model_key] = model
                continue
            if model.inherits_from not in models_already_validated:
                raise ValueError((f"Model {model.inherits_from} not found"
                                  " in models or the config is not in "
                                  "proper order"))
            # Let's apply inheritance
            base_model = models_already_validated[model.inherits_from].model_dump()
            base_types = [int, float, str, bool]
            dict_model = model.model_dump()
            dict_model = clear_default_values(dict_model)
            base_model = clear_default_values(base_model)
            for key, value in base_model.items():
                if key not in dict_model:
                    dict_model[key] = value
                # pylint: disable=unidiomatic-typecheck
                elif type(value) in base_types and type(value) == type(dict_model[key]):
                    pass
                elif isinstance(value, list) and isinstance(dict_model[key],list):
                    dict_model[key] = list(set(dict_model[key] + value))
                elif isinstance(value, dict) and isinstance(dict_model[key], dict):
                    dict_model[key] = {**value, **dict_model[key]}
                else:
                    raise ValueError((f"Model {model.name} has key {key} with value "
                                    f"{dict_model[key]} of type {type(dict_model[key])}"
                                    f" but base model {model.inherits_from} has"
                                    f" value {value} of type {type(value)}"))
            del dict_model["inherits_from"]
            model = ModelMetaInfo(**dict_model)
            models_already_validated[model_key] = model
        self.models = models_already_validated
        return self


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
