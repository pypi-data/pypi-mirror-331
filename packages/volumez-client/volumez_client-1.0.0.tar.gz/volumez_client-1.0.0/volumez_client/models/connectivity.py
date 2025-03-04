from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Connectivity")


@_attrs_define
class Connectivity:
    """
    Attributes:
        name (str):
        zones1 (str):
        systemtypes1 (str):
        zones2 (str):
        systemtypes2 (str):
        mediaprotocol (str):
        replicationprotocol (str):
        replicationbandwidth (Union[Unset, int]):
    """

    name: str
    zones1: str
    systemtypes1: str
    zones2: str
    systemtypes2: str
    mediaprotocol: str
    replicationprotocol: str
    replicationbandwidth: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        zones1 = self.zones1

        systemtypes1 = self.systemtypes1

        zones2 = self.zones2

        systemtypes2 = self.systemtypes2

        mediaprotocol = self.mediaprotocol

        replicationprotocol = self.replicationprotocol

        replicationbandwidth = self.replicationbandwidth

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "zones1": zones1,
                "systemtypes1": systemtypes1,
                "zones2": zones2,
                "systemtypes2": systemtypes2,
                "mediaprotocol": mediaprotocol,
                "replicationprotocol": replicationprotocol,
            }
        )
        if replicationbandwidth is not UNSET:
            field_dict["replicationbandwidth"] = replicationbandwidth

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        zones1 = d.pop("zones1")

        systemtypes1 = d.pop("systemtypes1")

        zones2 = d.pop("zones2")

        systemtypes2 = d.pop("systemtypes2")

        mediaprotocol = d.pop("mediaprotocol")

        replicationprotocol = d.pop("replicationprotocol")

        replicationbandwidth = d.pop("replicationbandwidth", UNSET)

        connectivity = cls(
            name=name,
            zones1=zones1,
            systemtypes1=systemtypes1,
            zones2=zones2,
            systemtypes2=systemtypes2,
            mediaprotocol=mediaprotocol,
            replicationprotocol=replicationprotocol,
            replicationbandwidth=replicationbandwidth,
        )

        connectivity.additional_properties = d
        return connectivity

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
