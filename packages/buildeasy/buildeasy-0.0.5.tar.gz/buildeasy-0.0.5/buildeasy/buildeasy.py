import sys
import inspect
import pickle
from functools import wraps
from typing import List, Optional
from Adaptor import Adaptor as a, modifiable

Adaptor: a = a()

class TransformationError(Exception):
    pass

class FileAsClass:
    _cache = {}

    def __init_subclass__(cls, **init_kwargs):
        super().__init_subclass__(**init_kwargs)

        caller_frame = sys._getframe(1)
        module_name = caller_frame.f_globals.get('__name__')

        if module_name is None:
            raise RuntimeError("Cannot determine module name from caller's frame.")
        module = sys.modules[module_name]

        if module_name in FileAsClass._cache:
            return FileAsClass._cache[module_name]

        init_signature = inspect.signature(cls.__init__)
        parameters = list(init_signature.parameters.values())[1:]
        init_args = {}

        for param in parameters:
            if param.name in init_kwargs:
                init_args[param.name] = init_kwargs[param.name]
            elif param.default is not param.empty:
                init_args[param.name] = param.default
            else:
                init_args[param.name] = None

        try:
            instance = cls(**init_args)
        except TypeError as e:
            raise TransformationError(f"Error instantiating {cls.__name__}: {e}") from e

        public_methods = []
        for attr_name, attr_value in cls.__dict__.items():
            if callable(attr_value) and not attr_name.startswith("_"):
                public_methods.append(attr_name)

        for attr_name, attr_value in cls.__dict__.items():
            if isinstance(attr_value, staticmethod):
                setattr(instance, attr_name, attr_value)
            elif isinstance(attr_value, classmethod):
                setattr(instance, attr_name, attr_value)

        instance.__all__ = public_methods + ['instance']
        instance.instance = instance

        for attr in ("__name__", "__package__", "__loader__", "__spec__", "__file__"):
            setattr(instance, attr, getattr(module, attr, None))

        for base_cls in cls.__mro__:
            if base_cls is not cls:
                for method_name, method_value in base_cls.__dict__.items():
                    if callable(method_value) and not method_name.startswith("_"):
                        setattr(instance, method_name, method_value)

        sys.modules[module_name] = instance
        FileAsClass._cache[module_name] = instance

        return instance

    def add_method(cls, method_name: str, method: callable):
        setattr(cls.instance, method_name, method)

    @staticmethod
    def load_from_cache(module_name: str):
        return FileAsClass._cache.get(module_name)

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    @classmethod
    def save(cls, filename: str):
        with open(filename, 'wb') as f:
            pickle.dump(cls.instance, f)

    @classmethod
    def load(cls, filename: str):
        with open(filename, 'rb') as f:
            cls.instance = pickle.load(f)

    @classmethod
    def scan(cls, directory: str, extension: str = ".py"):
        import os
        for filename in os.listdir(directory):
            if filename.endswith(extension):
                module_name = filename[:-3]
                try:
                    module = __import__(module_name)
                    FileAsClass(module)
                except Exception as e:
                    print(f"Failed to load plugin {module_name}: {e}")

    def __getattribute__(self, name):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            if hasattr(self, name):
                if isinstance(getattr(self, name), tuple):
                    return getattr(self, name)[0]
                else:
                    return getattr(self, name)
            else:
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")