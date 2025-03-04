from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RepairCmds")


@_attrs_define
class RepairCmds:
    """
    Attributes:
        cmds (list[str]):
        checksum (str):
        message (Union[Unset, str]):
    """

    cmds: list[str]
    checksum: str
    message: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cmds = self.cmds

        checksum = self.checksum

        message = self.message

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cmds": cmds,
                "checksum": checksum,
            }
        )
        if message is not UNSET:
            field_dict["message"] = message

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        cmds = cast(list[str], d.pop("cmds"))

        checksum = d.pop("checksum")

        message = d.pop("message", UNSET)

        repair_cmds = cls(
            cmds=cmds,
            checksum=checksum,
            message=message,
        )

        repair_cmds.additional_properties = d
        return repair_cmds

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
