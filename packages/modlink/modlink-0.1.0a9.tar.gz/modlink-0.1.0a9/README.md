[![PyPI version](https://img.shields.io/pypi/v/modlink.svg)](https://pypi.org/project/modlink/)
[![Python versions](https://img.shields.io/pypi/pyversions/modlink.svg)](https://pypi.org/project/modlink/)
[![License](https://img.shields.io/pypi/l/modlink.svg)](https://pypi.org/project/modlink/)
[![Wheel](https://img.shields.io/pypi/wheel/modlink.svg)](https://pypi.org/project/modlink/)

## Overview

ModLink is a flexible Python framework for building agents and actions. It defines interfaces for both natural language and computer interactions, enabling each agent to surface a set of context-specific actions.

See the [PATTERN.md](PATTERN.md) for definitions used in ModLink.

## Usage

For specific usage, see the [examples](examples/README.md) directory.

After defining your agent and actions, you can integrate additional tools. For instance, you can use [AgentArgParser](modlink/tools/agent_arg_parser.py) to enable command-line interaction with your agents.

```
cd modlink
poetry install
poetry shell
python example/agent.py -h
usage: agent.py [-h] {breaker,case,concat,filter,pad,replace,timestamp} ...

Edits text state

positional arguments:
  {breaker,case,concat,filter,pad,replace,timestamp}
                        Actions to perform.
    breaker             Breaks the text into lines using predefined character widths.
    case                Changes the case of the text.
    concat              Concatenates a string on the end of an existing text
    filter              Filters the text based on character types.
    pad                 Pads the text with text.
    replace             Replaces the text with a new value.
    timestamp           Adds a timestamp to the text.

options:
  -h, --help            show this help message and exit

python example/agent.py concat --text " I am here now"
INFO:root:Parsed action: {'action': 'concat', 'text': ' I am here now'}
Action result: 9035 Village Dr, Yosemite Valley, CA 95389, U.S.A. I am here now
```

## Example

```python
from modlink import Agent, agent_name
from modlink.tools.agent_arg_parser import AgentArgParser
import logging

from example.context import ExampleContext


@agent_name(
    name="example-agent",
    role="Edits text state",
)
class ExampleAgent(Agent[ExampleContext]):
    """
    An example implementation of an Agent.
    """

    def attach(self, context: ExampleContext):
        super().attach(context)

        # Add all the actions from a package to the agent
        self._action_registry.add_package("example.actions")

        # Alternatively, add actions individually
        # self._action_registry.add_action(ReplaceAction)


if __name__ == "__main__":
    # Run with python agent.py
    logging.basicConfig(level=logging.DEBUG)

    agent = ExampleAgent()
    agent.attach(ExampleContext())
    result = AgentArgParser(agent).parse_and_perform()
    print(f"Action result: {result}")
    agent.detach()
```

```python
from pydantic import Field
from modlink.action import Action, action_name

from example.context import ExampleContext


@action_name(
    name="concat",
    description="Concatenates a string on the end of an existing text",
)
class ConcatAction(Action):
    text: str = Field(description="The text to concatenate.")

    def perform(self, context: ExampleContext) -> str:
        context.text += self.text
        return context.text
```

## Contributing

We welcome contributions! If you'd like to contribute, please see our [CONTRIBUTING.md](CONTRIBUTING.md) for more information. 

## License

ModLink is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.