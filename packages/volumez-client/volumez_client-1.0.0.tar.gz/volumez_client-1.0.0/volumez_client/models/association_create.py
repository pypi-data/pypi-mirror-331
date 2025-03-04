from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AssociationCreate")


@_attrs_define
class AssociationCreate:
    """
    Attributes:
        name (Union[Unset, str]):
        volume (Union[Unset, str]):
        snapshot (Union[Unset, str]):
        mountpoint (Union[Unset, str]):
        selector (Union[Unset, str]):
    """

    name: Union[Unset, str] = UNSET
    volume: Union[Unset, str] = UNSET
    snapshot: Union[Unset, str] = UNSET
    mountpoint: Union[Unset, str] = UNSET
    selector: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        volume = self.volume

        snapshot = self.snapshot

        mountpoint = self.mountpoint

        selector = self.selector

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if volume is not UNSET:
            field_dict["volume"] = volume
        if snapshot is not UNSET:
            field_dict["snapshot"] = snapshot
        if mountpoint is not UNSET:
            field_dict["mountpoint"] = mountpoint
        if selector is not UNSET:
            field_dict["selector"] = selector

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name", UNSET)

        volume = d.pop("volume", UNSET)

        snapshot = d.pop("snapshot", UNSET)

        mountpoint = d.pop("mountpoint", UNSET)

        selector = d.pop("selector", UNSET)

        association_create = cls(
            name=name,
            volume=volume,
            snapshot=snapshot,
            mountpoint=mountpoint,
            selector=selector,
        )

        association_create.additional_properties = d
        return association_create

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
