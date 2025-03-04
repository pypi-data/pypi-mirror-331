from enum import Enum


class AlertAlertSeverity(str, Enum):
    CRITICAL = "Critical"
    FATAL = "Fatal"
    INFO = "Info"
    WARNING = "Warning"

    def __str__(self) -> str:
        return str(self.value)
