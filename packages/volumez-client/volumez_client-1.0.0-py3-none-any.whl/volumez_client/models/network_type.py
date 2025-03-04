from enum import Enum


class NetworkType(str, Enum):
    MANAGEMENT = "management"
    STORAGE = "storage"

    def __str__(self) -> str:
        return str(self.value)
