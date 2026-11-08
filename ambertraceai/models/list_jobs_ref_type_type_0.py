from enum import Enum


class ListJobsRefTypeType0(str, Enum):
    DOMAIN = "domain"
    PLATFORM = "platform"

    def __str__(self) -> str:
        return str(self.value)
