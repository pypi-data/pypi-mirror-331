from abc import ABC
from typing import Any, Dict, Generic, Type, TypeVar

from modlink.action import Action
from modlink.context import Context


def agent_name(name: str, role: str):
    def decorator(cls):
        cls.__agent_name__ = name
        cls.__agent_role__ = role
        return cls

    return decorator


TContext = TypeVar("TContext", bound="Context")


class Agent(Generic[TContext], ABC):
    """
    Abstract base class for Agents.

    Agents are responsible for performing actions and altering the context state.
    """

    @classmethod
    def name(cls):
        if not hasattr(cls, "__agent_name__"):
            raise RuntimeError("Agent must be decorated with @agentname")
        return cls.__agent_name__

    @classmethod
    def role(cls):
        if not hasattr(cls, "__agent_role__"):
            raise RuntimeError("Agent must be decorated with @agentname")
        return cls.__agent_role__

    def __init__(self):
        self._context: TContext = None
        from modlink.tools import ActionRegistry

        self._action_registry: ActionRegistry = ActionRegistry()

    @property
    def context(self) -> TContext:
        """
        Returns the current context of the agent.
        """
        if self._context is None:
            raise RuntimeError("Agent is not attached to any context")
        return self._context

    @property
    def actions(self) -> Dict[str, Type["Action"]]:
        """
        Returns the action map of the agent.
        """
        return self._action_registry.action_map

    def attach(self, context: TContext):
        """
        Lifecycle event that attaches the agent to a context.
        """
        self._context = context

    def perform(self, action: "Action") -> Any:
        """
        Perform the given action using the current context.
        """
        self._action_registry.validate(action)
        return action.perform(self.context)

    async def perform_async(self, action: "Action") -> Any:
        """
        Executes an action asynchronously.
        """
        return self.perform(action)

    def detach(self):
        """
        Lifecycle event that detaches the agent from a context.
        """
        self._action_registry.action_map.clear()
        self._context = None

    def schemas(self) -> Dict[str, Dict]:
        """
        Returns a schema for the agent.
        """
        return self._action_registry.schemas()

    def action_from_dict(self, value: Dict) -> "Action":
        """
        Converts a dictionary into an action.
        """
        return self._action_registry.from_dict(value)

    def action_from_json(self, value: str) -> "Action":
        """
        Converts a JSON string to an action.
        """
        return self._action_registry.from_json(value)

    def describe(self) -> Dict:
        """
        Describes the agent.
        """
        return {
            "name": self.__class__.name(),
            "role": self.__class__.role(),
            "actions": self.schemas(),
        }
