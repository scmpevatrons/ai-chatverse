"""
This module contains the meta information for a model
"""
from typing import Optional, Dict, Any, Union,Literal
import os
import sys
from importlib.util import spec_from_file_location, module_from_spec
from pydantic import Field, \
                        field_validator, \
                        model_validator, \
                        FieldValidationInfo, \
                        AliasChoices
from ui_elements.format_option import FormatOption
from ui_elements.base_element import StreamLitPydanticModel
from conversations.conversation import Conversation
from models.base_model import BaseLLMModel
from schema.shared_state import get_shared_state


class ModelMetaInfo(StreamLitPydanticModel):
    """
    This class is used to store the meta information for a model
    """
    base_dir:str = Field(validation_alias=AliasChoices('base_dir', "BaseDir"),
                                      description="The base dir of the app")
    key: Optional[str] = Field(description="The key for the model", default=None)
    name:str = Field(validation_alias=AliasChoices('name', 'Name'),
                     description="The name of the model",
                     min_length=3)
    description:str = Field(validation_alias=AliasChoices('description', "Description"),
                            description="The description of the model", min_length=20)
    llm_model_file: Optional[str] = Field(validation_alias=
                                          AliasChoices('llm_model_file', "LLMModelFile"),
                                          description="The model file", default=None)
    llm_model_class: Optional[str] = Field(validation_alias=
                                           AliasChoices('llm_model_class', "LLMModelClass"),
                                            description="The model class", default=None)
    supports_stream: bool = Field(validation_alias=
                                  AliasChoices('supports_stream', "SupportsStream"),
                                  description="Whether the model supports streaming",
                                  default=None)
    icon:str = Field(validation_alias=AliasChoices('icon', "Icon"),
                     description="The icon for the model",
                     default="llm_model.png")
    system_message: Optional[str] = Field(validation_alias=
                                          AliasChoices('system_message',
                                                       "SystemMessage"),
                                          description="The system message for the model",
                                          default=("You are a helpful assistant that"
                                                   " responds in Markdown format."))
    llm_arguments: Dict[str, Any] = Field(validation_alias=
                                                    AliasChoices('llm_arguments',
                                                                 "LLMArguments"),
                                                    description="The arguments for the LLM Model",
                                                     default={})
    memory_arguments: Dict[str, Any] = Field(validation_alias=
                                                       AliasChoices('memory_arguments',
                                                                    "MemoryArguments"),
                                                        description=("The arguments for the"
                                                                     " chat memory module"),
                                                        default={})
    required_llm_arguments:Dict[str,
                                    Literal["STRING", "INT", "FLOAT",
                                            "BOOL",
                                            "SECRET_STRING", "LONG_STRING",
                                            ]
                                ] = Field(validation_alias=
                                        AliasChoices('required_llm_arguments',
                                                    "RequiredLLMArguments"),
                                                    description=("The required arguments"
                                                                " for the model"),
                                                    default={})
    inherits_from: Optional[str] = Field(validation_alias=AliasChoices('inherits_from',
                                                                       "InheritsFrom"),
                                         description="The model to inherit from",
                                         default=None)

    is_persistent: bool = Field(validation_alias=AliasChoices('is_persistent', "IsPersistent"),
                                   description="Whether the model is persistent",
                                   default=True)

    _conversations:list[Conversation] = []


    def add_conversation(self, conversation:Conversation)->None:
        """
        This method is used to add a conversation
        
        Args:
            conversation: The conversation
        """
        self._conversations.append(conversation)


    def get_conversations(self)->list[Conversation]:
        """
        This method is used to get the conversations
        
        Returns:
            The conversations
        """
        return self._conversations


    def get_additional_custom_field_value(self, field_name:str)->Any:
        """
        This method is used to get the value for custom fields
        
        Args:
            field_name: The field name
        
        Returns:
            The field value
        """
        SHARED_CONFIG = get_shared_state()
        if field_name in SHARED_CONFIG:
            return SHARED_CONFIG[field_name]
        value = self.llm_arguments[field_name] if field_name in self.llm_arguments else None
        if value is not None:
            SHARED_CONFIG[field_name] = value
        return value


    def set_additional_custom_field_value(self, field_name:str, field_value:Any):
        """
        This method is used to set the value for custom fields
        
        Args:
            field_name: The field name
            field_value: The field value
        """
        self.llm_arguments[field_name] = field_value


    def additional_custom_fields_to_show(self)->list[Union[str, FormatOption]]:
        """
        This method is used to get the additional fields to show
        
        Returns:
             The additional fields to show
        """
        fields = []
        for argument, argument_type in self.required_llm_arguments.items():
            field = FormatOption(format_type=argument_type, title=argument, field_name=argument)
            fields.append(field)
        return fields


    def set_value_for_custom_fields(self, field_name:str, field_value:Any):
        """
        This method is used to set the value for custom fields
        
        Args:
            field_name: The field name
            field_value: The field value
        """
        SHARED_CONFIG = get_shared_state()
        SHARED_CONFIG[field_name] = field_value
        self.llm_arguments[field_name] = field_value


    @classmethod
    def fields_to_show(cls)->list[Union[str, FormatOption]]:
        """
        This method is used to get the fields to show
        
        Returns:
            The fields to show
        """
        schema:Dict[str, Any] = cls.model_json_schema()
        field_info:Dict[str, Any] = schema["properties"]
        fields = [
                    FormatOption(format_type="IMAGE_PATH", title=field_info["icon"]["description"],
                                 field_name="icon"),
                    FormatOption(format_type="STRING", title=field_info["name"]["description"],
                                 field_name="name"),
                    FormatOption(format_type="LONG_STRING",
                                 title=field_info["description"]["description"],
                                 field_name="description"),
                    FormatOption(format_type="LONG_STRING",
                                 title=field_info["system_message"]["description"],
                                 field_name="system_message"),
                    FormatOption(format_type="BOOL",
                                 title=field_info["supports_stream"]["description"],
                                 field_name="supports_stream"),
                    FormatOption(format_type="STRING",
                                 title=field_info["llm_model_file"]["description"],
                                 field_name="llm_model_file"),
                    FormatOption(format_type="STRING",
                                 title=field_info["llm_model_class"]["description"],
                                 field_name="llm_model_class"),
                    FormatOption(format_type="DICT",
                                 title=field_info["llm_arguments"]["description"],
                                 field_name="llm_arguments"),
                    FormatOption(format_type="DICT",
                                 title=field_info["memory_arguments"]["description"],
                                 field_name="memory_arguments"),
                    FormatOption(format_type="BOOL",
                                 title=field_info["is_persistent"]["description"],
                                 field_name="is_persistent")
                ]
        return fields

    @classmethod
    def fields_to_edit(cls)->list[Union[str, Dict[str, Dict[str, FormatOption]]]]:
        """
        This method is used to get the fields to edit
        
        Returns:
            The fields to edit
        """
        schema:Dict[str, Any] = cls.model_json_schema()
        field_info:Dict[str, Any] = schema["properties"]
        fields = [
                    FormatOption(format_type="IMAGE_PATH", title=field_info["icon"]["description"],
                                 field_name="icon"),
                    FormatOption(format_type="STRING", title=field_info["name"]["description"],
                                 field_name="name", create_value=""),
                    FormatOption(format_type="LONG_STRING",
                                 title=field_info["description"]["description"],
                                 field_name="description", create_value=""),
                    FormatOption(format_type="LONG_STRING",
                                 title=field_info["system_message"]["description"],
                                 field_name="system_message"),
                    FormatOption(format_type="BOOL",
                                 title=field_info["supports_stream"]["description"],
                                 field_name="supports_stream"),
                    FormatOption(format_type="DICT",
                                 title=field_info["llm_arguments"]["description"],
                                 field_name="llm_arguments"),
                    FormatOption(format_type="DICT",
                                 title=field_info["memory_arguments"]["description"],
                                 field_name="memory_arguments")
                ]
        return fields


    def additional_custom_fields_to_edit(self)->list[Union[str, FormatOption]]:
        """
        This method is used to get the additional fields to show
        
        Returns:
             The additional fields to show
        """
        fields = []
        for argument, argument_type in self.required_llm_arguments.items():
            field = FormatOption(format_type=argument_type, title=argument, field_name=argument)
            fields.append(field)
        return fields


    @field_validator("base_dir")
    @classmethod
    def validate_base_dir(cls, value:str)->str:
        """
        Validates the base dir
        
        Args:
            value: The value of the base dir
        
        Returns:
            The value of the base dir
        
        Raises:
            ValueError: If the base dir is not found
        """
        if not os.path.isdir(value):
            raise ValueError(f"Base dir {value} not found")
        return value


    @field_validator("icon")
    @classmethod
    def validate_icon(cls, value:str, field_info:FieldValidationInfo)->str:
        """
        Validates the icon
        
        Args:
            value: The value of the icon
            field_info: The field info object from pydantic.
        
        Returns:
            str: The value of the icon
        
        Raises:
            ValueError: If the icon is not found
        """
        value = os.path.join(field_info.data["base_dir"], "assets", value)
        if not os.path.isfile(value):
            raise ValueError(f"Icon file {value} not found")
        return value


    # pylint: disable=unused-argument
    @model_validator(mode="before")
    @classmethod
    def validate_model(cls, data:Dict, field_info:FieldValidationInfo)->Dict:
        """
        Validates the model
        
        Args:
            data: The data of the model
            field_info: The field info object from pydantic.
        Returns:
            The processed and validated data for the model
        Raises:
            ValueError: If the model is invalid
        """
        model_file_keys = ["llm_model_file", "LLMModelFile"]
        model_class_keys = ["llm_model_class", "LLMModelClass"]
        inherits_from_keys = ["inherits_from", "InheritsFrom"]
        model_file_key = None
        model_class_key = None
        inherits_from_key = None
        for key in model_file_keys:
            if key in data:
                model_file_key = key
                break
        for key in model_class_keys:
            if key in data:
                model_class_key = key
                break
        for key in inherits_from_keys:
            if key in data:
                inherits_from_key = key
                break
        if model_file_key is None or model_class_key is None:
            if inherits_from_key is None:
                raise ValueError(("Expected llm_model_file and llm_model_class"
                                  " or inherits_from to be present"))
            return data
        llm_model_file = os.path.join(data["base_dir"],
                                      "models", data[model_file_key])
        if os.path.isfile(llm_model_file) \
        and llm_model_file.endswith(".py") and model_class_key in data:
            class_name = data[model_class_key]
            module_name = f"models.{data[model_file_key].split('.', 1)[0]}"
            spec = spec_from_file_location(module_name,
                                            llm_model_file)
            module = module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            if hasattr(module, class_name) and \
            issubclass(getattr(module, class_name), BaseLLMModel):
                data[model_file_key] = llm_model_file
                return data
            raise ValueError((f"Class {data[model_class_key]} not found in model file"
                                    " {llm_model_file} or is not derived from BaseLLMModel"))
        raise ValueError((f"Model file {llm_model_file} not found or is not a python"
                            " file or doesn't have a corresponding model class"))
