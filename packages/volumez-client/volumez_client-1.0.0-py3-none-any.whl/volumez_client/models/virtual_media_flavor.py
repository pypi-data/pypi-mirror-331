from enum import Enum


class VirtualMediaFlavor(str, Enum):
    RAID1 = "raid1"
    STRIPPED = "stripped"

    def __str__(self) -> str:
        return str(self.value)
