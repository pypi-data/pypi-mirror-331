from enum import Enum


class VirtualMediaCreateFlavor(str, Enum):
    RAID1 = "raid1"
    SPLIT = "split"
    STRIPPED = "stripped"

    def __str__(self) -> str:
        return str(self.value)
