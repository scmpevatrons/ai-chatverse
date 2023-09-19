"""
This file is used to store the shared state of the config file
"""
from typing import Any
import streamlit as st

# Deprecating this class because it will leak keys in a multi-user environment
# class Singleton(type):
#     """
#     This class is used to make the config file a singleton
#     """
#     _instances = {}
#     def __call__(cls, *args, **kwargs):
#         if cls not in cls._instances:
#             cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
#         return cls._instances[cls]


# class SharedState(dict, metaclass=Singleton):
#     """
#     This class is used to store the shared state
#     """

def get_shared_state()->dict[str, Any]:
    """
    This method is used to get the shared state
    """
    if 'shared_state' not in st.session_state:
        st.session_state.shared_state = {}
    return st.session_state.shared_state
