
"""
This file contains the FormatOption class
"""
from typing import Any, Optional, Literal
from pydantic import BaseModel, Field, model_validator



class FormatOption(BaseModel):
    """
    This class is used to store the format fields
    """
    format_type:Literal["STRING", "INT", "FLOAT",
                        "BOOL", "LIST", "DICT",
                        "SECRET_STRING", "LONG_STRING",
                        "STRING_CHOICE",
                        "IMAGE_PATH"] = Field(description="The format type")
    create_value:Optional[Any] = Field(description="The create value", default=None)
    title:str = Field(description="The title", default=None)
    value:Any = Field(description="The value of the data", default=None)
    field_name:str = Field(description="The field name")
    choices:Optional[list[str]] = Field(description="The choices", default=None)


    @model_validator(mode="after")
    def validate_option(self)->'FormatOption':
        """
        This method is used to validate the option

        Returns:
            The validated option
        """
        if self.format_type == "STRING_CHOICE":
            if self.choices is None or len(self.choices) == 0:
                raise ValueError("The choices must be specified")
        return self

