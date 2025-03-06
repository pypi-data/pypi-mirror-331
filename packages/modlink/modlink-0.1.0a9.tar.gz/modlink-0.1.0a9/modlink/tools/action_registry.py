import importlib
import inspect
import json
import pkgutil
from typing import Dict, List, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from modlink.action import Action


class ActionRegistry:
    def __init__(self):
        self.action_map: Dict[str, Type["Action"]] = {}

    def add(self, action: Type["Action"]):
        """
        Add a single Action class to the action map.

        :param action: The Action class to add.
        """
        self.action_map[action.name()] = action

    def add_all(self, *actions: Type["Action"]):
        """
        Add multiple Action classes to the action map.

        :param actions: A variable number of Action classes to add.
        """
        for action in actions:
            self.add(action)

    def remove(self, action: Type["Action"]) -> bool:
        """
        Remove a single Action class from the action map.

        :param action: The Action class to remove.
        :return: True if the action was removed, False if it was not found.
        """
        return self.action_map.pop(action.name(), None) is not None

    def remove_all(self, *actions: Type["Action"]) -> List[Type["Action"]]:
        """
        Remove multiple Action classes from the action map.

        :param actions: A variable number of Action classes to remove.
        :return: A list of Action classes that were successfully removed.
        """
        return [action for action in actions if self.remove(action)]

    def schemas(self) -> List[Dict]:
        """
        Get the action schemas for all registered actions.

        :return: A list of action schemas.
        """
        return [action.action_schema() for action in self.action_map.values()]

    def from_dict(self, value: Dict) -> "Action":
        """
        Create an Action instance from a dictionary.

        :param value: A dictionary representation of the action.
        :return: An instance of the appropriate Action subclass.
        """
        name = value.get("action")
        action_class = self.action_map.get(name)
        if not action_class:
            raise ValueError(f"Action '{name}' is not registered.")
        return action_class.model_validate(value)

    def from_json(self, value: str) -> "Action":
        """
        Create an Action instance from a JSON string.

        :param value: A JSON string representation of the action.
        :return: An instance of the appropriate Action subclass.
        """
        data = json.loads(value)
        return self.from_dict(data)

    def validate(self, action: "Action"):
        """
        Validate that the given Action is registered.

        :param action: The Action instance to validate.
        :raises ValueError: If the action is not registered.
        """
        name = action.name()
        if name not in self.action_map:
            raise ValueError(f"Unsupported action: {name}")

    def add_package(self, package_name: str) -> List[Type["Action"]]:
        """
        Load and register all Action subclasses from the specified package.

        :param package_name: The package name (e.g., 'texteditor.actions').
        :return: A list of Action classes that were registered.
        """
        action_classes = self._get_from_package(package_name)
        self.add_all(*action_classes)
        return action_classes

    def remove_package(self, package_name: str) -> List[Type["Action"]]:
        """
        Remove all Action subclasses from the specified package.

        :param package_name: The package name (e.g., 'texteditor.actions').
        :return: A list of Action classes that were removed.
        """
        action_classes = self._get_from_package(package_name)
        self.remove_all(*action_classes)
        return action_classes

    def _get_from_package(self, package_name: str) -> List[Type["Action"]]:
        """
        Recursively load all Action subclasses from the specified package.

        :param package_name: The package name to search for Action subclasses.
        :return: A list of discovered Action classes.
        """
        from modlink import Action

        action_classes: List[Type[Action]] = []

        def recursive_get_from_package(current_package_name: str):
            package = importlib.import_module(current_package_name)
            for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
                full_module_name = f"{current_package_name}.{module_name}"
                if is_pkg:
                    recursive_get_from_package(full_module_name)
                else:
                    module = importlib.import_module(full_module_name)
                    for _, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, Action) and obj is not Action:
                            action_classes.append(obj)

        recursive_get_from_package(package_name)
        return action_classes
