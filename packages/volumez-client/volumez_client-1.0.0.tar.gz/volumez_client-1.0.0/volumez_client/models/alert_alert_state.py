from enum import Enum


class AlertAlertState(str, Enum):
    ACKNOWLEDGED = "Acknowledged"
    ACTIVE = "Active"
    CLEARED = "Cleared"

    def __str__(self) -> str:
        return str(self.value)
