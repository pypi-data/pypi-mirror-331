# /Users/robinsongarcia/projects/gnomonic/projection/base/registry.py

from typing import Any, Dict, Optional, Type, Union
import logging

logger = logging.getLogger('spherical_projections.registry')

class RegistryBase(type):
    """
    Metaclass to automatically register classes in a central REGISTRY dictionary.
    """

    REGISTRY = {}

    def __new__(cls, name, bases, attrs):
        """
        Create a new class and register it in the REGISTRY.
        """
        new_cls = type.__new__(cls, name, bases, attrs)
        cls.REGISTRY[new_cls.__name__] = new_cls
        return new_cls

    @classmethod
    def get_registry(cls):
        """
        Retrieve the dictionary of all registered classes.
        
        Returns:
            dict: Copy of the class registry.
        """
        return dict(cls.REGISTRY)

class BaseRegisteredClass(metaclass=RegistryBase):
    """
    Base class that uses the RegistryBase metaclass for automatic registration.
    """
    pass