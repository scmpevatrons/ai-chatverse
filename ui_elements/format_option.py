
"""
This file contains the FormatOption class
"""
from typing import Any, Optional, Literal
from pydantic import BaseModel, Field



class FormatOption(BaseModel):
    """
    This class is used to store the format fields
    """
    format_type:Literal["STRING", "INT", "FLOAT",
                        "BOOL", "LIST", "DICT",
                        "SECRET_STRING", "LONG_STRING",
                        "IMAGE_PATH"] = Field(description="The format type")
    create_value:Optional[Any] = Field(description="The create value", default=None)
    title:str = Field(description="The title", default=None)
    value:Any = Field(description="The value of the data", default=None)
    field_name:str = Field(description="The field name")
