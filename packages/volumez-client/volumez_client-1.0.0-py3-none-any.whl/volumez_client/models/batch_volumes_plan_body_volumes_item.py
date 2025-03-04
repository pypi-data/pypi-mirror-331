from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BatchVolumesPlanBodyVolumesItem")


@_attrs_define
class BatchVolumesPlanBodyVolumesItem:
    """
    Attributes:
        size (int): volume size in GiB Example: 10.
        policy (Union[Unset, str]): policy name for the planned volume
        zone (Union[Unset, str]):  Example: us-east-1a.
    """

    size: int
    policy: Union[Unset, str] = UNSET
    zone: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        size = self.size

        policy = self.policy

        zone = self.zone

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "Size": size,
            }
        )
        if policy is not UNSET:
            field_dict["Policy"] = policy
        if zone is not UNSET:
            field_dict["Zone"] = zone

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        size = d.pop("Size")

        policy = d.pop("Policy", UNSET)

        zone = d.pop("Zone", UNSET)

        batch_volumes_plan_body_volumes_item = cls(
            size=size,
            policy=policy,
            zone=zone,
        )

        batch_volumes_plan_body_volumes_item.additional_properties = d
        return batch_volumes_plan_body_volumes_item

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
