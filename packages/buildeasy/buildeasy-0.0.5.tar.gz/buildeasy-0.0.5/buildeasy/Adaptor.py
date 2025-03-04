import inspect
import os
import sys
import threading
from functools import wraps

# Registry to store modifiable functions and classes
MODIFIABLES = {}
LOCK = threading.Lock()  # Ensure thread safety


def modifiable(obj):
    """Marks a function or class as modifiable. If applied to a class, all its methods become modifiable."""
    module = obj.__module__
    if inspect.isclass(obj):
        MODIFIABLES.setdefault(module, {})
        for name, method in obj.__dict__.items():
            if callable(method) and not name.startswith("_"):
                MODIFIABLES[module][name] = method
    else:
        MODIFIABLES.setdefault(module, {})[obj.__name__] = obj
    return obj


class Adaptor:
    """Modifies functions and classes in real-time and updates source files."""

    @staticmethod
    def update(module: str, name: str, new_code: str):
        """Updates a function/class in memory and in its source file."""
        with LOCK:  # Prevent race conditions
            if module not in MODIFIABLES or name not in MODIFIABLES[module]:
                raise ValueError(f"{name} in {module} is not modifiable.")

            mod = sys.modules.get(module)
            if not mod:
                raise ImportError(f"Module {module} is not loaded.")

            backup = MODIFIABLES[module][name]  # Store backup before modifying
            sandbox = {"__builtins__": {}}  # Restrict execution scope

            try:
                exec(new_code, mod.__dict__, sandbox)
                new_func = sandbox.get(name)
                if not new_func:
                    raise ValueError(f"New code did not define '{name}'.")
                MODIFIABLES[module][name] = new_func
                Adaptor._edit_file(module, name, new_code)
            except Exception as e:
                MODIFIABLES[module][name] = backup  # Revert on failure
                raise RuntimeError(f"Failed to update {name} in {module}: {e}") from e

    @staticmethod
    def _edit_file(module: str, name: str, new_code: str):
        """Replaces a function/class definition in its source file."""
        mod = sys.modules.get(module)
        if not mod or not hasattr(mod, "__file__"):
            raise RuntimeError(f"Cannot find source file for {module}.")

        file_path = mod.__file__
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Source file {file_path} not found.")

        with open(file_path, "r") as f:
            lines = f.readlines()

        start, end = None, None
        for i, line in enumerate(lines):
            if line.strip().startswith(f"def {name}(") or line.strip().startswith(f"class {name}"):
                start = i
                break

        if start is None:
            raise ValueError(f"{name} not found in {file_path}.")

        for i in range(start + 1, len(lines)):
            if lines[i].strip() and not lines[i].startswith(" "):
                end = i
                break

        if end is None:
            end = len(lines)

        lines[start:end] = [line + "\n" for line in new_code.split("\n")]

        with open(file_path, "w") as f:
            f.writelines(lines)

    @staticmethod
    def find_and_replace(module: str, target: str, replacement: str):
        """Finds and replaces a specific line in the source file."""
        with LOCK:
            mod = sys.modules.get(module)
            if not mod or not hasattr(mod, "__file__"):
                raise RuntimeError(f"Cannot find source file for {module}.")

            file_path = mod.__file__
            with open(file_path, "r") as f:
                lines = f.readlines()

            lines = [line.replace(target, replacement) if target in line else line for line in lines]

            with open(file_path, "w") as f:
                f.writelines(lines)

    @staticmethod
    def get_code(module: str):
        """Returns the entire source code of a module."""
        mod = sys.modules.get(module)
        if not mod or not hasattr(mod, "__file__"):
            raise RuntimeError(f"Cannot find source file for {module}.")

        with open(mod.__file__, "r") as f:
            return f.read()

    @staticmethod
    def list_modifiable(module: str):
        """Lists all modifiable functions and classes in a module."""
        return list(MODIFIABLES.get(module, {}).keys())
