from enum import Enum


class VolumeFlavor(str, Enum):
    FILEDIRECT = "filedirect"
    REGULAR = "regular"

    def __str__(self) -> str:
        return str(self.value)
