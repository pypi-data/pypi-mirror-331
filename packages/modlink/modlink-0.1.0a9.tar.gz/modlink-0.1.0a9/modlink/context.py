from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from modlink.platform import Platform


class Context:
    """
    Context are the injectable dependencies for an Agent.
    This can include storage interfaces, network servies,
    or internal state. Contexts can also include access to
    other agents.
    """

    _platform: "Platform" = None

    @property
    def platform(self) -> "Platform":
        """
        Returns the platform associated with the context.
        """
        if self._platform is None:
            raise RuntimeError("Context is not attached to a Platform")
        return self._platform
