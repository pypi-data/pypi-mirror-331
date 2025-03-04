from enum import Enum


class SnapshotConsistency(str, Enum):
    APPLICATION = "application"
    CRASH = "crash"

    def __str__(self) -> str:
        return str(self.value)
