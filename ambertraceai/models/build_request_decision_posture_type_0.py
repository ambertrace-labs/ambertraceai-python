from enum import Enum


class BuildRequestDecisionPostureType0(str, Enum):
    DEFAULT_ALLOW = "default_allow"
    FAIL_CLOSED = "fail_closed"

    def __str__(self) -> str:
        return str(self.value)
