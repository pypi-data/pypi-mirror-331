import sys
from typing import Any


def get_parent_class(cls: type) -> Any:
    return sys.modules[cls.__module__].__dict__[cls.__qualname__.split('.')[0]]
