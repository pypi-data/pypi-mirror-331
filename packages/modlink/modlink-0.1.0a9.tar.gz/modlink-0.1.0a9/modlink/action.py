from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, model_validator

from modlink.context import Context


def action_name(name: str, description: str):
    def decorator(cls):
        cls.__action_name__ = name
        cls.__action_description__ = description
        return cls

    return decorator


class Action(BaseModel, ABC):
    """
    Abstract base class representing an Action.

    This class is intended to be used as a base for defining actions
    that agents can execute.
    """

    action: str = Field(default=None)

    @model_validator(mode="before")
    def assign_action(cls, values):
        values["action"] = cls.name()
        return values

    @classmethod
    def name(cls):
        if not hasattr(cls, "__action_name__"):
            raise RuntimeError(f"{cls.__name__} must be decorated by @action_name")
        return cls.__action_name__

    @classmethod
    def description(cls):
        if not hasattr(cls, "__action_description__"):
            raise RuntimeError(f"{cls.__name__} must be decorated by @action_name")
        return cls.__action_description__

    @classmethod
    def action_schema(cls, by_alias=True):
        schema = super().model_json_schema(by_alias=by_alias)
        del schema["title"]
        schema["required"] = ["action"] + schema.get("required", [])
        schema["properties"]["action"] = {
            "type": "string",
            "value": cls.name(),
            "description": "Constant value to indicate the action type.",
        }
        schema.update({"description": cls.description()})
        return schema

    @abstractmethod
    def perform(self, platform: "Context") -> None:
        """
        Method to be implemented by each Action subclass to perform its action.

        Args:
          context: The context in which the action is performed.
        """
        pass
