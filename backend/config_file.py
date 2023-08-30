"""
This module is used to parse and store the config file
"""
from typing import Any, Dict
from pydantic import BaseModel, Field, model_validator
from models.meta_info import ModelMetaInfo


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


class ConfigFile(BaseModel):
    """
    This class is used to store the information for the config file
    """

    models:Dict[str, ModelMetaInfo] = Field(validation_alias="Models", description="The models")
    keys:set[str] = Field(validation_alias="Keys", description="The model keys", default=set())
    base_dir:str = Field(validation_alias="BaseDir", description="The base directory", default=None)


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
            model_key = None
            if "models" in data:
                model_key = "models"
            elif "Models" in data:
                model_key = "Models"
            if model_key is None:
                raise ValueError("Models key not found in config file")
            models = data[model_key]
            for model_key, model in models.items():
                if "base_dir" not in model:
                    model["base_dir"] = data["base_dir"]
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
