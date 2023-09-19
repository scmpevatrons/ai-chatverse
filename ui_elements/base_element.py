"""
This module contains the base class for all the streamlit UI elements
"""
import os
from copy import deepcopy
from typing import Any, Union, Optional, Literal, Callable
from pydantic import BaseModel, ValidationError, PrivateAttr
from pydantic.fields import ModelPrivateAttr
import streamlit as st
from ui_elements.format_option import FormatOption

# pylint: disable=too-many-public-methods
class StreamLitPydanticModel(BaseModel):
    """
    This class is used to automatically generate the streamlit UI for a pydantic model
    """

    _FIELD_TYPES = PrivateAttr(default=["STRING", "INT", "FLOAT",
               "BOOL", "LIST", "DICT",
               "SECRET_STRING", "LONG_STRING",
               "IMAGE_PATH"])
    _meta_info:Optional[dict[str, FormatOption]]



    def additional_custom_fields_to_show(self)->list[Union[str, FormatOption]]:
        """
        This method is used to get the additional fields to be shown by the model
        
        Returns:
             The additional fields to show
        """
        return []


    def get_additional_custom_field_value(self, field_name:str)->Any:
        """
        This method is used to get the value for custom fields
        
        Args:
            field_name: The field name
        
        Returns:
            The field value
        
        Raises:
            NotImplementedError: This method is not implemented and needs to be
        """
        raise NotImplementedError(("This method is not implemented and needs to be"
                                      " implemented by the child class"))


    def set_additional_custom_field_value(self, field_name:str, field_value:Any):
        """
        This method is used to set the value for custom fields
        
        Args:
            field_name: The field name
            field_value: The field value
        """
        raise NotImplementedError(("This method is not implemented and needs to be"
                                      " implemented by the child class"))


    def set_value_for_custom_fields(self, field_name:str, field_value:Any)->None:
        """
        This method is used to set the value for custom fields
        
        Args:
            field_name: The field name
            field_value: The field value
        """
        raise NotImplementedError(("This method is not implemented and needs to be"
                                   " implemented by the child class"))


    def get_field_value(self, field_name:str)->Any:
        """
        This method is used to get the value for a field
        
        Args:
            field_name: The field name
        
        Returns:
            The field value
        """
        return getattr(self, field_name)


    def set_field_value(self, field_name:str, field_value:Any)->None:
        """
        This method is used to set the value for a field
        
        Args:
            field_name: The field name
            field_value: The field value
        """
        current_value = self.get_field_value(field_name)
        try:
            setattr(self, field_name, field_value)
            self.__pydantic_validator__.validate_python(self.model_dump(), self_instance=self)
        except Exception as exc:
            setattr(self, field_name, current_value)
            raise exc


    @classmethod
    def get_value(cls, value:Union[Any, FormatOption])->Any:
        """
        This function returns the value of the format option
        
        Args:
            value: The value of the format option
        
        Returns:
            Any: The value of the format option
        """
        if isinstance(value, FormatOption):
            return value.value
        return value


    @classmethod
    def fields_to_show(cls)->list[Union[str, FormatOption]]:
        """
        This method is used to get the fields to show
        
        Returns:
           The fields to show
        """
        return cls.model_json_schema()["properties"].keys()


    @classmethod
    def fields_to_edit(cls)->list[Union[str, FormatOption]]:
        """
        This method is used to get the fields to edit
        
        Returns:
            The fields to edit
        """
        return cls.model_json_schema()["properties"].keys()


    def additional_custom_fields_to_edit(self)->list[Union[str, FormatOption]]:
        """
        This method is used to get the additional fields to show
        
        Returns:
             The additional fields to show
        """
        return []


    @classmethod
    def get_default_value(cls, value:Optional[Any]=None,
                          field_type:Optional[Literal["STRING", "INT", "FLOAT",
                                                    "BOOL", "LIST", "DICT",
                                                    "SECRET_STRING", "LONG_STRING",
                                                    "IMAGE_PATH"]]=None)->Any:
        """
        This function returns the default value of the object
        
        Args:
            value: The value of the object
            field_type: The field type
        
        Returns:
            The default value of the object
        """
        default_values_for_field_types = {
            "STRING": "",
            "INT": 0,
            "FLOAT": 0.0,
            "BOOL": False,
            "LIST": [],
            "DICT": {},
            "SECRET_STRING": "",
            "LONG_STRING": "",
            "IMAGE_PATH": ""
        }
        default_value_based_on_data_type = {
            str: "",
            int: 0,
            float: 0.0,
            bool: False,
            list: [],
            dict: {},
        }
        if value:
            default_value = default_value_based_on_data_type.get(type(value))
            if default_value is None:
                raise NotImplementedError(f"Unknown type {type(value)}")
            return default_value
        if field_type:
            default_value = default_values_for_field_types[field_type]
            if default_value is None:
                raise NotImplementedError(f"Unknown field type {field_type}")
            return default_value


    @classmethod
    def find_target_to_modify(cls,
                              keys:list[str],
                              object_to_search:Any,
                              operation:Callable[[Union[str, int], Any], None],
                              *args)->None:
        """
        This function finds the target to modify
        this function is called in case of update, delete operations
        
        Args:
            keys: The list of keys to search
            object_to_search: The object to search
            operation: The operation to perform
        """
        if len(keys) == 1:
            operation(keys[0], object_to_search, *args)
            return
        object_to_search = cls.get_value(object_to_search)
        if isinstance(object_to_search, dict):
            cls.find_target_to_modify(keys[1:], object_to_search[keys[0]],
                                    operation, *args)
        elif isinstance(object_to_search, list):
            cls.find_target_to_modify(keys[1:], object_to_search[int(keys[0])],
                                    operation, *args)
        else:
            raise NotImplementedError(f"{type(object_to_search)} is not supported")


    @classmethod
    def update_array(cls, type_key:str)->None:
        """
        This function is called when user clicks on the add new item button
        
        Args:
            type_key: The key of the type of the item to add
        """
        field_type = st.session_state[type_key]
        model_meta_dict = st.session_state['model_meta_dict']
        keys = type_key.split("|")[1:]
        cls.find_target_to_modify(keys,
                                   model_meta_dict,
                                   cls.insert_operation,
                                   cls.get_default_value(field_type=field_type),
                                   field_type)


    @classmethod
    def update_dict(cls, value_key:str, type_key:str)->None:
        """
        This function is called when user clicks on the add new key button
        
        Args:
            value_key: The key of the value of the item to add
            type_key: The key of the type of the item to add
        """
        value = st.session_state[value_key]
        st.session_state[value_key] = ""
        field_type = st.session_state[type_key]
        if value == "":
            st.toast("Please enter a valid key", icon="⚠️")
            return
        model_meta_dict = st.session_state['model_meta_dict']
        keys = value_key.split("|")[1:]
        cls.find_target_to_modify(keys,model_meta_dict,
                                  cls.insert_operation,
                                  value, field_type)



    def get_serialised_model_data(self,
                                   view_mode:bool=False,
                                   create_mode=False)->dict[str, FormatOption]:
        """
        This function returns the serialised model meta information
        
        Args:
            view_mode: Whether the model is in view mode
            create_mode: Whether the model is in create mode
        
        Returns:
            The serialised model meta information
        """
        model_meta:dict[str, Any] = {}
        schema:dict = self.model_json_schema()["properties"]
        if view_mode:
            fields = self.fields_to_show()
        else:
            fields = self.fields_to_edit()
        for field in fields:
            if isinstance(field, FormatOption):
                value = deepcopy(self.get_field_value(field.field_name))
                if field.create_value is not None and create_mode:
                    value = self.get_default_value(field_type=field.format_type)
                field.value = value
            else:
                field_name = field
                title = field
                field_type = schema[field_name]['type']
                value = deepcopy(self.get_field_value(field))
                field = FormatOption(format_type=field_type,
                                     field_name=field_name,
                                     title=title, field_value=value)
            model_meta[field.field_name] = field
        return model_meta


    @classmethod
    def render_list_object(cls, field_name:str,
                           header:str, value:list[Any],
                           edit_mode:bool=False,
                           key_prefix:str="")->None:
        """
        This function renders the list object
        
        Args:
            field_name: The field name of the object
            header: The header of the object
            value: The value of the object
            edit_mode: Whether the object is in edit mode
            key_prefix: The prefix to the key
        """
        with st.expander(header):
            for i, item in enumerate(value):
                cls.render_object(f"{i}", f"{i}",
                            item, edit_mode=edit_mode,
                            key_prefix=cls.get_field_key(key_prefix, field_name),
                                                          delete=True)
            if edit_mode:
                _, middle, right = st.columns([1, 1, 1])
                with middle:
                    type_key = cls.get_field_key(
                                cls.get_field_key(key_prefix, field_name),
                                "item_type")
                    field_types = cls._FIELD_TYPES
                    if isinstance(field_types, ModelPrivateAttr):
                        field_types = field_types.default
                    st.selectbox("New Item Type", field_types,
                                 key=type_key)
                with right:
                    st.write("\n")
                    button_key = cls.get_field_key(
                                    cls.get_field_key(
                                                        key_prefix,
                                                        field_name),
                                                    "add_item_key")
                    st.button("Add New Item", key=button_key,
                            on_click=cls.update_array,
                            args=(type_key,))


    @classmethod
    def delete_operation(cls, key:Union[str, int],
                         object_to_search:Any, *args)->None:
        """
        This function deletes the key from the object
        
        Args:
            key: The key to delete
            object_to_search: The object to search
        """
        object_to_search = cls.get_value(object_to_search) 
        if isinstance(object_to_search, dict):
            del object_to_search[key]
        else:
            del object_to_search[int(key)]


    # pylint: disable=unused-argument
    @classmethod
    def insert_operation(cls, key:Union[str, int], object_to_search:Any,
                        insert_field_name:Any, insert_type:str)->None:
        """
        This function inserts the key into the object
        
        Args:
            key: The key to insert
            object_to_search: The object to search
            insert_value: The value to insert
            insert_type: The type of the value to insert
        """
        new_value = FormatOption(format_type=insert_type,
                                field_name=str(insert_field_name),
                                title=str(insert_field_name),
                                value=cls.get_default_value(field_type=insert_type))
        object_to_search = cls.get_value(object_to_search)
        if isinstance(object_to_search, dict):
            object_to_search[insert_field_name] = new_value
        else:
            new_value.field_name = str(len(object_to_search))
            new_value.title = str(len(object_to_search))
            object_to_search.append(new_value)


    @classmethod
    def render_dict_object(cls, field_name:str, header:str,
                        value:dict[str, Any],
                        edit_mode:bool=False, key_prefix:str="")->None:
        """
        This function renders the dict object
        
        Args:
            field_name: The field name of the object
            header: The header of the object
            value: The value of the object
            edit_mode: Whether the object is in edit mode
            key_prefix: The prefix to the key
        """
        with st.expander(header):
            for key, item in value.items():
                cls.render_object(key, key, item, edit_mode=edit_mode,
                            key_prefix=cls.get_field_key(key_prefix, field_name),
                            delete=True)
            if edit_mode:
                left, middle, right = st.columns([1, 1, 1])
                with left:
                    value_key = cls.get_field_key(
                                    cls.get_field_key(key_prefix, field_name),
                                    "dict_key")
                    st.text_input("New Key Name", key=value_key)
                with middle:
                    type_key = cls.get_field_key(
                                    cls.get_field_key(key_prefix, field_name),
                                    "dict_type")
                    field_types = cls._FIELD_TYPES
                    if isinstance(field_types, ModelPrivateAttr):
                        field_types = field_types.default
                    st.selectbox("New Value Type", field_types, key=type_key)
                with right:
                    st.write("\n")
                    key = cls.get_field_key(
                                cls.get_field_key(key_prefix, field_name),
                                "dict_add_key")
                    st.button("Add New Key", key=key,
                            on_click=cls.update_dict,
                            args=(value_key, type_key))


    @classmethod
    def render_secret_string_object(cls, field_name:str,
                                    header:str, value:str,
                                    edit_mode:bool=False, key_prefix:str="")->None:
        """
        This function renders the secret string object
        
        Args:
            field_name: The field name of the object
            header: The header of the object
            value: The value of the object
            edit_mode: Whether the object is in edit mode
            key_prefix: The prefix to the key
        """
        disabled = not edit_mode
        st.text_input(header, value,
                    key=cls.get_field_key(key_prefix, field_name),
                    disabled=disabled,
                    type="password")


    @classmethod
    def render_long_string_object(cls,
                                  field_name:str,
                                  header:str,
                                  value:str,
                                  edit_mode:bool=False,
                                  key_prefix:str="")->None:
        """
        This function renders the long string object
        
        Args:
            field_name: The field name of the object
            header: The header of the object
            value: The value of the object
            edit_mode: Whether the object is in edit mode
            key_prefix: The prefix to the key
        """
        disabled = not edit_mode
        st.text_area(header, value,
                    key=cls.get_field_key(key_prefix, field_name) ,
                    disabled=disabled)


    # pylint: disable=unused-argument
    @classmethod
    def render_image_path_object(cls,
                                 field_name:str,
                                 header:str, image_path:str,
                                 edit_mode:bool=False,
                                 key_prefix:str="")->None:
        """
        This function renders the image path object

        Args:
            field_name: The field name of the object
            header: The header of the object
            value: The value of the object
            edit_mode: Whether the object is in edit mode
            key_prefix: The prefix to the key
        """
        _, middle_col, _ = st.columns([1, 2, 1])
        with middle_col:
            st.image(image_path, caption=header)


    @classmethod
    def render_string_object(cls, field_name:str, header:str,
                             value:str, edit_mode:bool=False,
                             key_prefix:str="")->None:
        """
        This function renders the string object

        Args:
            field_name: The field name of the object
            header: The header of the object
            value: The value of the object
            edit_mode: Whether the object is in edit mode
            key_prefix: The prefix to the key
        """
        disabled = not edit_mode
        st.text_input(header, value,
                    key=cls.get_field_key(key_prefix, field_name),
                    disabled=disabled)


    @classmethod
    def render_number_object(cls, field_name:str,
                             header:str,
                             value:float,
                             edit_mode:bool=False,
                             key_prefix:str="")->None:
        """
        This function renders the number object

        Args:
            field_name: The field name of the object
            header: The header of the object
            value: The value of the object
            edit_mode: Whether the object is in edit mode
            key_prefix: The prefix to the key
        """
        disabled = not edit_mode
        st.number_input(header, value=value,
                        key=cls.get_field_key(key_prefix, field_name),
                        disabled=disabled)


    @classmethod
    def render_bool_object(cls, field_name:str,
                        header:str, value:bool,
                        edit_mode:bool=False,
                        key_prefix:str="")->None:
        """
        This function renders the bool object
        
        Args:
            field_name: The field name of the object
            header: The header of the object
            value: The value of the object
            edit_mode: Whether the object is in edit mode
            key_prefix: The prefix to the key
        """
        disabled = not edit_mode
        allowed_values = [str(False), str(True)]
        st.selectbox(header, allowed_values,
                    index=allowed_values.index(str(value)),
                    key=cls.get_field_key(key_prefix, field_name),
                    disabled=disabled)


    @classmethod
    def render_object_internal(cls, field_name:str, header:str, value:Any,
                field_type:Optional[Literal["STRING", "INT", "FLOAT",
                                            "BOOL", "LIST", "DICT",
                                            "SECRET_STRING", "LONG_STRING",
                                            "IMAGE_PATH"]]=None,
                key_prefix:str="",
                edit_mode:bool=False)->None:
        """
        This function renders the object
        
        Args:
            field_name: The field name of the object
            header: The header of the object
            value: The value of the object
            edit_mode: Whether the object is in edit mode
            key_prefix: The prefix to the key
        """
        if field_type is None:
            if isinstance(value, (str, bool)):
                if isinstance(value, bool):
                    cls.render_bool_object(field_name, header, value, edit_mode, key_prefix)
                else:
                    if "icon" in header.lower() and os.path.exists(value):
                        cls.render_image_path_object(field_name, header,
                                                      value, edit_mode, key_prefix)
                    else:
                        if len(value) < 20:
                            cls.render_string_object(field_name, header,
                                                      value, edit_mode, key_prefix)
                        else:
                            cls.render_long_string_object(field_name, header,
                                                           value, edit_mode, key_prefix)
            elif isinstance(value, (int, float)):
                cls.render_number_object(field_name, header,
                                          value, edit_mode, key_prefix)
            elif isinstance(value, list):
                cls.render_list_object(field_name, header,
                                        value, edit_mode, key_prefix)
            elif isinstance(value, dict):
                cls.render_dict_object(field_name, header,
                                        value, edit_mode, key_prefix)
            else:
                raise NotImplementedError(f"Unknown type {type(value)}")
        else:
            {
                "STRING": cls.render_string_object,
                "INT": cls.render_number_object,
                "FLOAT": cls.render_number_object,
                "BOOL": cls.render_bool_object,
                "LIST": cls.render_list_object,
                "DICT": cls.render_dict_object,
                "SECRET_STRING": cls.render_secret_string_object,
                "LONG_STRING": cls.render_long_string_object,
                "IMAGE_PATH": cls.render_image_path_object
            }[field_type](field_name, header, value, edit_mode, key_prefix)


    @classmethod
    def delete_object(cls, key:str, model_meta_dict:dict[str, FormatOption])->None:
        """
        This function is called when user clicks on the delete button
        
        Args:
            key: The key of the object to delete
            model_meta_dict: The model meta information
        """
        parts_of_key = key.split("|")[1:]
        cls.find_target_to_modify(parts_of_key[1:],
                            cls.get_value(model_meta_dict[parts_of_key[0]]),
                            cls.delete_operation)


    @classmethod
    def get_field_key(cls, key_prefix:str, field_name)->str:
        """
        This function returns the field key
        
        Args:
            key_prefix: The prefix to the key
            field_name: The field name
        
        Returns:
            The field key
        """
        return "|".join([key_prefix, field_name])


    @classmethod
    def get_data_from_meta(cls, meta_info:dict[str, FormatOption],
                           key_prefix:str="")->dict[str, Any]:
        """
        This function gets the data from the streamlit session state
        based on the meta information
        
        Args:
            meta_info: The meta information
            key_prefix: The prefix to the key in session state
        Returns:
            The data in the same structure as the meta information from session state
        """
        meta_info = cls.get_value(meta_info)
        if isinstance(meta_info, dict):
            response = {}
            for key in meta_info:
                value = cls.get_data_from_meta(meta_info[key],
                                            "|".join([key_prefix, key]))
                if value is not None:
                    response[key] = value
        elif isinstance(meta_info, list):
            response = []
            for i, item in enumerate(meta_info):
                value = cls.get_data_from_meta(item,
                                            "|".join([key_prefix, str(i)]))
                if value is not None:
                    response.append(value)
        else:
            # If Key is not found return the default value
            if key_prefix not in st.session_state:
                return meta_info
            if isinstance(meta_info, bool):
                response = st.session_state[key_prefix] == "True"
            else:
                response = st.session_state[key_prefix]
        return response


    @classmethod
    def render_object(cls, field_name:str,
                      header:str, value:Any,
                      field_type:Optional[Literal["STRING", "INT", "FLOAT",
                                                "BOOL", "LIST", "DICT",
                                                "SECRET_STRING", "LONG_STRING",
                                                "IMAGE_PATH"]]=None,
                        key_prefix:str="",
                        edit_mode:bool=False,
                        delete:bool=False)->None:
        """
        This function renders the object
        
        Args:
            header: The header of the object
            value: The value of the object
            field_type: Tells the type of the field (optional)
            key_prefix: The prefix to the key
            edit_mode: Whether the object is in edit mode
            delete: Whether the object can be deleted
        """
        if isinstance(value, FormatOption):
            field_type = value.format_type
            field_name = value.field_name
            value = value.value
        if edit_mode and delete:
            item_col, delete_col = st.columns([92, 8])
            with item_col:
                cls.render_object_internal(field_name, header, value,
                                           field_type, key_prefix, edit_mode)
            with delete_col:
                st.write("")
                st.write("")
                field_key = cls.get_field_key(key_prefix, field_name)
                delete_key = cls.get_field_key(field_key, "delete")
                meta_info = cls._meta_info
                st.button("🗑️", key=delete_key, on_click=cls.delete_object,
                        args=(field_key, meta_info))
        else:
            cls.render_object_internal(field_name, header, value,
                                        field_type,
                                        key_prefix, edit_mode)



    def render_model_in_view_mode(self, model_meta_info:dict[str, FormatOption])->None:
        """
        This function renders the model to view
        
        Args:
            model_meta_info: The model meta information
        """
        for field in model_meta_info:
            self.render_object(field, model_meta_info[field].title,
                              model_meta_info[field].value,
                              model_meta_info[field].format_type,
                              edit_mode=False)


    @classmethod
    def render_model_in_create_mode(cls, model_meta_info:dict[str, FormatOption])->None:
        """
        This function renders the model in create mode
        
        Args:
            model_meta_info: The model meta information
        """
        cls._meta_info = model_meta_info
        for field in model_meta_info:
            cls.render_object(field, model_meta_info[field].title,
                               model_meta_info[field].value,
                               model_meta_info[field].format_type,
                               edit_mode=True)

    @classmethod
    def create_model(cls, model_dict:dict[str, FormatOption])->Optional['StreamLitPydanticModel']:
        """
        This function creates the model
        
        Args:
            model_dict: The model meta information
        
        Returns:
            The model object
        """
        try:
            model_meta_dict = cls.get_data_from_meta(model_dict)
            return cls(**model_meta_dict)
        except ValidationError as validation_error:
            msgs = []
            for error in validation_error.errors():
                field_names = ""
                if error['loc']:
                    field_names = ",".join(error['loc']) + ": "
                msgs.append(f"{field_names}{error['msg']}")
            error_message = "\n".join(msgs)
            st.toast(error_message, icon="⚠️")
            return None


    def validate_edit_and_save_state(self, model_dict:dict[str, FormatOption])->bool:
        """
        This function validates the edit
        
        Args:
            model_dict: The model meta information
        
        Returns:
            Whether the edit is valid
        """
        model_meta_dict = self.get_data_from_meta(model_dict)
        try:
            for key, value in model_meta_dict.items():
                self.set_field_value(key, value)
        except ValidationError as validation_error:
            msgs = []
            for error in validation_error.errors():
                field_names = ""
                if error['loc']:
                    field_names = ",".join(error['loc']) + ": "
                msgs.append(f"{field_names}{error['msg']}")
            error_message = "\n".join(msgs)
            st.toast(error_message, icon="⚠️")
            return False
        return True



    def render_model_in_edit_mode(self, model_dict:dict[str, FormatOption])->None:
        """
        This function renders the model create view

        Args:
            model_dict: The model meta information
        """
        # pylint: disable=protected-access
        self.__class__._meta_info = model_dict
        for field in model_dict:
            self.render_object(field,
                        model_dict[field].title, model_dict[field].value,
                        model_dict[field].format_type, edit_mode=True)
            

    def render_sidebar(self)->None:
        """
        This function renders the sidebar
        """
        fields_to_show = self.additional_custom_fields_to_edit()
        if not fields_to_show:
            return
        with st.sidebar:
            st.title("Required Fields")
            for field in fields_to_show:

                if isinstance(field, FormatOption):
                    field_name = field.field_name
                    field_type = field.format_type
                else:
                    field_name = field
                    field_type = None
                field_value = self.get_additional_custom_field_value(field_name)
                if field_value is None:
                    field_value = self.get_default_value(field_type=field_type)
                self.render_object(field_name, field_name, field_value, field_type=field_type,
                                    edit_mode=True)


    def set_value_from_sidebar(self):
        """
        This function sets the value from the sidebar
        The value is set from the session state
        """
        fields_to_show = self.additional_custom_fields_to_edit()
        if not fields_to_show:
            return
        for field in fields_to_show:
            if isinstance(field, FormatOption):
                field_name = field.field_name
            else:
                field_name = field
            value = st.session_state[self.get_field_key("", field_name)]
            self.set_additional_custom_field_value(field_name, value)
