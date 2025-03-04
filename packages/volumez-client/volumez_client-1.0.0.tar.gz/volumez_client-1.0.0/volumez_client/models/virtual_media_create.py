from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.virtual_media_create_flavor import VirtualMediaCreateFlavor
from ..types import UNSET, Unset

T = TypeVar("T", bound="VirtualMediaCreate")


@_attrs_define
class VirtualMediaCreate:
    """
    Attributes:
        selector (Union[Unset, str]):
        flavor (Union[Unset, VirtualMediaCreateFlavor]):
    """

    selector: Union[Unset, str] = UNSET
    flavor: Union[Unset, VirtualMediaCreateFlavor] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        selector = self.selector

        flavor: Union[Unset, str] = UNSET
        if not isinstance(self.flavor, Unset):
            flavor = self.flavor.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if selector is not UNSET:
            field_dict["selector"] = selector
        if flavor is not UNSET:
            field_dict["flavor"] = flavor

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        selector = d.pop("selector", UNSET)

        _flavor = d.pop("flavor", UNSET)
        flavor: Union[Unset, VirtualMediaCreateFlavor]
        if isinstance(_flavor, Unset):
            flavor = UNSET
        else:
            flavor = VirtualMediaCreateFlavor(_flavor)

        virtual_media_create = cls(
            selector=selector,
            flavor=flavor,
        )

        virtual_media_create.additional_properties = d
        return virtual_media_create

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
