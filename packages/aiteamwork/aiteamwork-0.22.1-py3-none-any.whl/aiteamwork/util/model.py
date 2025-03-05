import re
from typing import Any

from pydantic import BaseModel, TypeAdapter

CLASS_NAME_REGEX = regex = re.compile(r"<class '([^']+)'>")


def get_model_name(model: type[BaseModel] | TypeAdapter) -> str:
    if callable(model) and issubclass(model, BaseModel):
        return model.__module__ + "." + model.__name__
    elif isinstance(model, TypeAdapter):
        as_str = str(model._type)
        if as_str.startswith("<class "):
            match = CLASS_NAME_REGEX.search(as_str)
            if match:
                return match.group(1)
        return as_str
    else:
        raise ValueError(
            f"Model {model} must be a class based on pydantic BaseModel or an instance of pydantic TypeAdapter"
        )


def get_model_name_from_value(value: Any) -> str:
    if isinstance(value, BaseModel):
        return get_model_name(value.__class__)
    else:
        return get_model_name(TypeAdapter(type(value)))
