from datetime import datetime, timezone


# This class is used to wrap the datetime.now() function
# so that it can be mocked in tests.
class AgentTime:
    @classmethod
    def now(cls) -> datetime:
        """
        Returns the current time as a datetime object.
        """
        return datetime.now()

    @classmethod
    def timestamp(cls) -> float:
        """
        Returns the current time in UTC as a timestamp.
        """
        return datetime.now(timezone.utc).timestamp()

    @classmethod
    def datestring(cls) -> str:
        """
        Returns the current date as a YYYY-MM-DD string.
        """
        return cls.now().strftime("%Y-%m-%d")
