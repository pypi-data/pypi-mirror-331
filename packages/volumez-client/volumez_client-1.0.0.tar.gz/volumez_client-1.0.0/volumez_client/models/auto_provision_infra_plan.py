from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.auto_provision_infra_plan_os_type import AutoProvisionInfraPlanOsType
from ..types import UNSET, Unset

T = TypeVar("T", bound="AutoProvisionInfraPlan")


@_attrs_define
class AutoProvisionInfraPlan:
    """
    Attributes:
        instance_type (Union[Unset, str]):  Example: c6gd.2xlarge.
        instance_count (Union[Unset, int]):  Example: 10.
        availability_zones (Union[Unset, list[str]]):
        os_type (Union[Unset, AutoProvisionInfraPlanOsType]):
        price (Union[Unset, int]):  Example: 10.
    """

    instance_type: Union[Unset, str] = UNSET
    instance_count: Union[Unset, int] = UNSET
    availability_zones: Union[Unset, list[str]] = UNSET
    os_type: Union[Unset, AutoProvisionInfraPlanOsType] = UNSET
    price: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        instance_type = self.instance_type

        instance_count = self.instance_count

        availability_zones: Union[Unset, list[str]] = UNSET
        if not isinstance(self.availability_zones, Unset):
            availability_zones = self.availability_zones

        os_type: Union[Unset, str] = UNSET
        if not isinstance(self.os_type, Unset):
            os_type = self.os_type.value

        price = self.price

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if instance_type is not UNSET:
            field_dict["instanceType"] = instance_type
        if instance_count is not UNSET:
            field_dict["instanceCount"] = instance_count
        if availability_zones is not UNSET:
            field_dict["availabilityZones"] = availability_zones
        if os_type is not UNSET:
            field_dict["osType"] = os_type
        if price is not UNSET:
            field_dict["price"] = price

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        instance_type = d.pop("instanceType", UNSET)

        instance_count = d.pop("instanceCount", UNSET)

        availability_zones = cast(list[str], d.pop("availabilityZones", UNSET))

        _os_type = d.pop("osType", UNSET)
        os_type: Union[Unset, AutoProvisionInfraPlanOsType]
        if isinstance(_os_type, Unset):
            os_type = UNSET
        else:
            os_type = AutoProvisionInfraPlanOsType(_os_type)

        price = d.pop("price", UNSET)

        auto_provision_infra_plan = cls(
            instance_type=instance_type,
            instance_count=instance_count,
            availability_zones=availability_zones,
            os_type=os_type,
            price=price,
        )

        auto_provision_infra_plan.additional_properties = d
        return auto_provision_infra_plan

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
