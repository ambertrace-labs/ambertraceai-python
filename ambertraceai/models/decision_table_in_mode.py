from enum import Enum


class DecisionTableInMode(str, Enum):
    LADDER = "ladder"
    PARTITION = "partition"

    def __str__(self) -> str:
        return str(self.value)
