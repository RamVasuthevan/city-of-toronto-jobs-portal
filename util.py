import inspect
import json
import sys
from datetime import date
from types import ModuleType
from typing import Callable, List

from models import Job


class CustomJSONEncoder(json.JSONEncoder):
    """JSON encoder that handles Job models and dates"""
    def default(self, obj):
        if isinstance(obj, Job):
            return obj.model_dump()
        if isinstance(obj, date):
            return obj.strftime('%b %d, %Y')
        return super().default(obj)




def get_all_functions_in_module(module: ModuleType) -> List[Callable]:
    return [name for name, obj in module.__dict__.items() if inspect.isfunction(obj)]
