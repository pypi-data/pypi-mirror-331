from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.network_type import NetworkType
from ..types import UNSET, Unset

T = TypeVar("T", bound="Network")


@_attrs_define
class Network:
    """
    Attributes:
        name (str):
        type_ (NetworkType):
        ipstart (str):
        ipend (str):
        zone (Union[Unset, str]):
    """

    name: str
    type_: NetworkType
    ipstart: str
    ipend: str
    zone: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        type_ = self.type_.value

        ipstart = self.ipstart

        ipend = self.ipend

        zone = self.zone

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "type": type_,
                "ipstart": ipstart,
                "ipend": ipend,
            }
        )
        if zone is not UNSET:
            field_dict["zone"] = zone

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        type_ = NetworkType(d.pop("type"))

        ipstart = d.pop("ipstart")

        ipend = d.pop("ipend")

        zone = d.pop("zone", UNSET)

        network = cls(
            name=name,
            type_=type_,
            ipstart=ipstart,
            ipend=ipend,
            zone=zone,
        )

        network.additional_properties = d
        return network

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
