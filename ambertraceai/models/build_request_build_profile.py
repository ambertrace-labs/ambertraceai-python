from enum import Enum


class BuildRequestBuildProfile(str, Enum):
    FULL = "full"
    PREDICTION_ONLY = "prediction_only"

    def __str__(self) -> str:
        return str(self.value)
