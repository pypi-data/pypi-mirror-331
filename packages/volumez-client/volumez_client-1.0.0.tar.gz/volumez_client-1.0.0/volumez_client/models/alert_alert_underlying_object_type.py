from enum import Enum


class AlertAlertUnderlyingObjectType(str, Enum):
    ATTACHMENT = "Attachment"
    MEDIA = "Media"
    NODE = "Node"
    SNAPSHOT = "Snapshot"
    VOLUME = "Volume"

    def __str__(self) -> str:
        return str(self.value)
