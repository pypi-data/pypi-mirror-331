from enum import Enum


class AutoProvisionInfraPlanOsType(str, Enum):
    LINUX = "Linux"
    RHEL = "Rhel"
    UBUNTU = "Ubuntu"

    def __str__(self) -> str:
        return str(self.value)
