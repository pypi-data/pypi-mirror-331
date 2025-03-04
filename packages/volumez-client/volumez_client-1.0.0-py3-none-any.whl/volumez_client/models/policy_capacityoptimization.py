from enum import Enum


class PolicyCapacityoptimization(str, Enum):
    BALANCED = "balanced"
    CAPACITY = "capacity"
    PERFORMANCE = "performance"

    def __str__(self) -> str:
        return str(self.value)
