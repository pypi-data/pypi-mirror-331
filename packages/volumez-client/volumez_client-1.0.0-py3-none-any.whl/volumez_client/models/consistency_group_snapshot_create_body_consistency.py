from enum import Enum


class ConsistencyGroupSnapshotCreateBodyConsistency(str, Enum):
    APPLICATION = "application"
    CRASH = "crash"

    def __str__(self) -> str:
        return str(self.value)
