from enum import Enum


class VolumeType(str, Enum):
    BLOCK = "block"
    FILE = "file"

    def __str__(self) -> str:
        return str(self.value)
