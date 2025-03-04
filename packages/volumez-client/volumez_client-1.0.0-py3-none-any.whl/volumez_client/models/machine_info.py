from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MachineInfo")


@_attrs_define
class MachineInfo:
    """
    Attributes:
        instanceid (Union[Unset, str]):
        instancetype (Union[Unset, str]):  Example: c6gd.2xlarge.
        controladdress (Union[Unset, str]):
        imageid (Union[Unset, str]):
        zone (Union[Unset, str]):
        sha (Union[Unset, str]):
    """

    instanceid: Union[Unset, str] = UNSET
    instancetype: Union[Unset, str] = UNSET
    controladdress: Union[Unset, str] = UNSET
    imageid: Union[Unset, str] = UNSET
    zone: Union[Unset, str] = UNSET
    sha: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        instanceid = self.instanceid

        instancetype = self.instancetype

        controladdress = self.controladdress

        imageid = self.imageid

        zone = self.zone

        sha = self.sha

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if instanceid is not UNSET:
            field_dict["instanceid"] = instanceid
        if instancetype is not UNSET:
            field_dict["instancetype"] = instancetype
        if controladdress is not UNSET:
            field_dict["controladdress"] = controladdress
        if imageid is not UNSET:
            field_dict["imageid"] = imageid
        if zone is not UNSET:
            field_dict["zone"] = zone
        if sha is not UNSET:
            field_dict["sha"] = sha

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        instanceid = d.pop("instanceid", UNSET)

        instancetype = d.pop("instancetype", UNSET)

        controladdress = d.pop("controladdress", UNSET)

        imageid = d.pop("imageid", UNSET)

        zone = d.pop("zone", UNSET)

        sha = d.pop("sha", UNSET)

        machine_info = cls(
            instanceid=instanceid,
            instancetype=instancetype,
            controladdress=controladdress,
            imageid=imageid,
            zone=zone,
            sha=sha,
        )

        machine_info.additional_properties = d
        return machine_info

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
