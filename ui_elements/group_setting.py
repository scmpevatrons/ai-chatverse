"""
This module is used to store the meta GPT setting for the startup
"""
from typing import Any, Dict, Union
from pydantic import Field
from ui_elements.base_element import StreamLitPydanticModel
from ui_elements.format_option import FormatOption
from schema.shared_state import get_shared_state


# pylint: disable=abstract-method
class MetaGPTSetting(StreamLitPydanticModel):
    """
    This class is used to store the meta GPT setting for the startup
    """
    investment: float = Field(description="Upper Limit in OpenAI API usage in USD", default=3)
    implement: bool = Field(description="Generate Application Code",
                            default=True)
    code_review: bool = Field(description="Enable Code Review", default=True)
    openai_api_key: str = Field(description="The OpenAI API key", default="")
    run_tests: bool = Field(description="Generate Test Cases for the application", default=False)

    def set_field_value(self, field_name: str, field_value: Any) -> None:
        """
        This method is used to set the value for a field

        Args:
            field_name: The field name
            field_value: The field value
        """
        SHARED_CONFIG:Dict[str, Any] = get_shared_state()
        if field_name == "openai_api_key":
            SHARED_CONFIG[field_name] = field_value
        return super().set_field_value(field_name, field_value)


    def get_field_value(self, field_name:str)->Any:
        """
        This method is used to get the value for a field
        
        Args:
            field_name: The field name
        
        Returns:
            The field value
        """
        SHARED_CONFIG:Dict[str, Any] = get_shared_state()
        if field_name == "openai_api_key":
            return SHARED_CONFIG.get("openai_api_key", "")
        return getattr(self, field_name)


    @classmethod
    def fields_to_edit(cls)->list[Union[str, FormatOption]]:
        """
        This method is used to get the fields to edit
        
        Returns:
            The fields to edit
        """
        schema:Dict[str, Any] = cls.model_json_schema()
        field_info:Dict[str, Any] = schema["properties"]
        return [
            FormatOption(format_type="FLOAT", title=field_info["investment"]["description"],
                                 field_name="investment"),
            FormatOption(format_type="BOOL", title=field_info["implement"]["description"],
                                    field_name="implement"),
            FormatOption(format_type="BOOL", title=field_info["code_review"]["description"], 
                                    field_name="code_review"),
            FormatOption(format_type="SECRET_STRING",
                         title=field_info["openai_api_key"]["description"],
                                    field_name="openai_api_key"),
            FormatOption(format_type="BOOL", title=field_info["run_tests"]["description"],
                                    field_name="run_tests")
        ]
