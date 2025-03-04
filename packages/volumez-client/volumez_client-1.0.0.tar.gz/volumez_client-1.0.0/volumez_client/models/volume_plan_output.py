from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.plan import Plan


T = TypeVar("T", bound="VolumePlanOutput")


@_attrs_define
class VolumePlanOutput:
    """
    Attributes:
        message (Union[Unset, str]):
        success (Union[Unset, bool]):
        plans (Union[Unset, list['Plan']]):
    """

    message: Union[Unset, str] = UNSET
    success: Union[Unset, bool] = UNSET
    plans: Union[Unset, list["Plan"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        message = self.message

        success = self.success

        plans: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.plans, Unset):
            plans = []
            for plans_item_data in self.plans:
                plans_item = plans_item_data.to_dict()
                plans.append(plans_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if message is not UNSET:
            field_dict["Message"] = message
        if success is not UNSET:
            field_dict["Success"] = success
        if plans is not UNSET:
            field_dict["Plans"] = plans

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.plan import Plan

        d = src_dict.copy()
        message = d.pop("Message", UNSET)

        success = d.pop("Success", UNSET)

        plans = []
        _plans = d.pop("Plans", UNSET)
        for plans_item_data in _plans or []:
            plans_item = Plan.from_dict(plans_item_data)

            plans.append(plans_item)

        volume_plan_output = cls(
            message=message,
            success=success,
            plans=plans,
        )

        volume_plan_output.additional_properties = d
        return volume_plan_output

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
