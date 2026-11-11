from enum import Enum


class CertifiedOutputRefSourceType(str, Enum):
    PREDICTION = "prediction"
    VERIFY_PROPERTY = "verify_property"

    def __str__(self) -> str:
        return str(self.value)
