import asyncio
from typing import Dict, Any, Callable, List

from modlink.agent import Agent
from modlink.context import Context
from modlink.action import Action


class Platform:
    def __init__(self):
        self._context: "Context" = None
        self._agents: Dict[str, "Agent"] = {}
        self._subscriptions: Dict[str, List[Callable[[Any], None]]] = {}
        self._event_loop = asyncio.get_event_loop()

    def attach(self, context: "Context"):
        context._platform = self
        self._context = context
        for agent in self._agents.values():
            agent.attach(context)

    @property
    def context(self) -> "Context":
        return self._context

    def perform(self, agent_name: str, action: "Action"):
        agent = self.agent(agent_name)
        if agent:
            agent.perform(self, action)
        else:
            raise ValueError(f"Agent is not registered: {agent_name}")

    async def perform_async(self, agent_name: str, action: "Action"):
        self.perform(agent_name, action)

    def detach(self):
        context = self.context
        self._context = None
        for agent in self._agents.values():
            if agent.context is context:
                agent.detach()
        if context is not None:
            context._platform = None

    def register_agent(self, agent: "Agent"):
        self._agents[agent.name()] = agent
        self._subscriptions[agent.name()] = []
        if self._context:
            agent.attach(self._context)

    def register_agents(self, agents: List["Agent"]):
        for agent in agents:
            self.register_agent(agent)

    def unregister_agent(self, agent: "Agent"):
        if self._context and agent.context() is self._context:
            agent.detach()
        if agent.name() in self._agents:
            del self._agents[agent.name()]
            del self._subscriptions[agent.name()]

    def unregister_all_agents(self):
        self._agents.clear()
        self._subscriptions.clear()

    def subscribe(self, agent_name: str, callback: Callable[[Any], None]):
        if agent_name in self._subscriptions:
            self._subscriptions[agent_name].append(callback)

    def unsubscribe(self, agent_name: str, callback: Callable[[Any], None]):
        if agent_name in self._subscriptions:
            self._subscriptions[agent_name].remove(callback)

    def agents(self) -> Dict[str, "Agent"]:
        return self._agents

    def agent(self, agent_name: str) -> "Agent":
        return self._agents[agent_name]

    def notify(self, agent_name: str, event: Any):
        if agent_name in self._subscriptions:
            for callback in self._subscriptions[agent_name]:
                self._event_loop.call_soon(callback, event)

    def actions(self) -> Dict[str, "Action"]:
        actions = {}
        for agent in self._agents.values():
            actions.update(agent.actions)
        return actions
