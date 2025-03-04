from enum import Enum


class AlertAlertType(str, Enum):
    PROCESSFAILED = "ProcessFailed"
    STATECHANGE = "StateChange"
    THRESHOLDREACHED = "ThresholdReached"

    def __str__(self) -> str:
        return str(self.value)
