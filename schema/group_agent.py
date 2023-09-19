import os
from typing import Any
from pydantic import BaseModel, Field, model_validator
from ui_elements.group_setting import MetaGPTSetting
from utils.util import get_field_name
from backend.metagpt import run_metagpt

class GroupAgentCharacter(BaseModel):
    """
    This class is used to store the group agent character information
    """
    name: str = Field(validation_alias="Name", description="The name of the group agent character")
    icon: str = Field(validation_alias="Icon", description="The icon of the group agent character")
    description: str = Field(validation_alias="Description",
                             description="The description of the group agent character")
    role: str = Field(validation_alias="Role", description="The role of the group agent character")
    base_dir: str = Field(description="The base directory of the App", default=None)

    @model_validator(mode='after')
    def validate_character(self)->'GroupAgentCharacter':
        """
        This method is used to validate the group agent character
        """
        icon_path = os.path.join(self.base_dir, "assets", self.icon)
        if not os.path.exists(icon_path):
            raise ValueError(f"Icon path {icon_path} does not exist")
        self.icon = icon_path
        return self

class GroupExample(BaseModel):
    """
    This class is used to store the group example information
    """
    name: str = Field(validation_alias="Name",
                      description="The name of the group example")
    description: str = Field(validation_alias="Description",
                             description="The description of the group example")

class GroupAgent(BaseModel):
    """
    This class is used to store the group agent information
    """
    name: str = Field(validation_alias="Name", description="The name of the group agent")
    icon: str = Field(validation_alias="Icon", description="The icon of the group agent")
    description: str = Field(validation_alias="Description",
                             description="The description of the group agent")
    usage_description: str = Field(validation_alias="UsageDescription",
                                   description="The usage description of the group agent")
    characters:list[GroupAgentCharacter] = Field(validation_alias="Characters",
                                                 description="The characters of the group agent")
    base_dir: str = Field(validation_alias="BaseDir",
                          description="The base directory of the group agent", default=None)
    examples:list[GroupExample] = Field(validation_alias="Examples",
                                        description="The examples of the group agent")
    setting: MetaGPTSetting = Field(validation_alias="Setting",
                                    description="The setting of the group agent",
                                    default_factory=MetaGPTSetting)
    flow_diagram: str = Field(validation_alias="FlowDiagram",
                              description="The flow diagram of the group agent")

    def run(self, idea:str)->None:
        """
        This method is used to run the group agent
        
        Args:
            idea: The idea
        """
        run_metagpt(self.setting, self.characters, idea)
        

    @model_validator(mode='before')
    @classmethod
    def validate_icon_and_add_base_dir(cls, data: Any) -> Any:
        """
        This method is used to validate the models
        
        Args:
            data: The data
        
        Returns:
            The validated data
        """
        if isinstance(data, dict):
            base_dir_field_name = get_field_name(data, ["base_dir", "BaseDir"])
            if base_dir_field_name is None:
                raise ValueError("BaseDir key not found in config file")
            base_dir = data[base_dir_field_name]
            icon_field_name = get_field_name(data, ["icon", "Icon"])
            if icon_field_name is None:
                raise ValueError("Icon key not found in config file")
            icon = data[icon_field_name]
            icon_path = os.path.join(base_dir, "assets", icon)
            if not os.path.exists(icon_path):
                raise ValueError(f"Icon path {icon_path} does not exist")
            data[icon_field_name] = icon_path
            flow_diagram_field_name = get_field_name(data, ["flow_diagram", "FlowDiagram"])
            if flow_diagram_field_name is None:
                raise ValueError("Icon key not found in config file")
            flow_diagram = data[flow_diagram_field_name]
            flow_diagram_path = os.path.join(base_dir, "assets", flow_diagram)
            if not os.path.exists(flow_diagram_path):
                raise ValueError(f"Flow diagram path {flow_diagram_path} does not exist")
            data[flow_diagram_field_name] = flow_diagram_path
            character_field_name = get_field_name(data, ["characters", "Characters"])
            if character_field_name is None:
                raise ValueError("Characters key not found in config file")
            characters = data[character_field_name]
            for character in characters:
                if "base_dir" not in character:
                    character["base_dir"] = base_dir
        return data

    @model_validator(mode='after')
    def validate_group(self)->'GroupAgent':
        """
        This method is used to validate the group agent
        
        Returns:
            The group agent object
        
        Raises:
            InvalidConfigError: If the group agent is invalid
        """
        if len(self.characters) == 0:
            raise ValueError(f"Group agent {self.name} has no characters")
        self_count = 0
        for character in self.characters:
            if character.role.lower() == "user":
                self_count += 1
        if self_count == 0:
            raise ValueError(f"Group agent {self.name} has no user character")
        if self_count > 1:
            raise ValueError(f"Group agent {self.name} has more than one user character")
        if len(self.characters) < 2:
            raise ValueError(f"Group agent {self.name} has less than two characters")
        return self
    
    def get_character(self, role:str)->GroupAgentCharacter:
        """
        This method is used to get the character with the given role

        Args:
            role: The role of the character
        Returns:
            The character with the given role
        Raises:
            ValueError: If the character with the given role is not found
        """
        for character in self.characters:
            if character.role.lower() == role.lower():
                return character
        raise ValueError(f"Character with role {role} not found in group agent {self.name}")