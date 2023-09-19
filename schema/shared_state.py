"""
This file is used to store the shared state of the config file
"""

class Singleton(type):
    """
    This class is used to make the config file a singleton
    """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SharedState(dict, metaclass=Singleton):
    """
    This class is used to store the shared state
    """

SHARED_CONFIG = SharedState()
