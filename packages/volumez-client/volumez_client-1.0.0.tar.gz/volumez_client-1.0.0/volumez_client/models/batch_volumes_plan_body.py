from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.batch_volumes_plan_body_volumes_item import BatchVolumesPlanBodyVolumesItem


T = TypeVar("T", bound="BatchVolumesPlanBody")


@_attrs_define
class BatchVolumesPlanBody:
    """
    Attributes:
        volumes (Union[Unset, list['BatchVolumesPlanBodyVolumesItem']]):
        capacity_group (Union[Unset, str]): capacity groups to create the volume from (optional)
        default_zone (Union[Unset, str]): zone parameter for all volumes that dont have zone parameter
        default_policy (Union[Unset, str]): policy parameter for all volumes that dont have policy parameter defined in
            their input
    """

    volumes: Union[Unset, list["BatchVolumesPlanBodyVolumesItem"]] = UNSET
    capacity_group: Union[Unset, str] = UNSET
    default_zone: Union[Unset, str] = UNSET
    default_policy: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        volumes: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.volumes, Unset):
            volumes = []
            for volumes_item_data in self.volumes:
                volumes_item = volumes_item_data.to_dict()
                volumes.append(volumes_item)

        capacity_group = self.capacity_group

        default_zone = self.default_zone

        default_policy = self.default_policy

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if volumes is not UNSET:
            field_dict["Volumes"] = volumes
        if capacity_group is not UNSET:
            field_dict["CapacityGroup"] = capacity_group
        if default_zone is not UNSET:
            field_dict["DefaultZone"] = default_zone
        if default_policy is not UNSET:
            field_dict["DefaultPolicy"] = default_policy

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.batch_volumes_plan_body_volumes_item import BatchVolumesPlanBodyVolumesItem

        d = src_dict.copy()
        volumes = []
        _volumes = d.pop("Volumes", UNSET)
        for volumes_item_data in _volumes or []:
            volumes_item = BatchVolumesPlanBodyVolumesItem.from_dict(volumes_item_data)

            volumes.append(volumes_item)

        capacity_group = d.pop("CapacityGroup", UNSET)

        default_zone = d.pop("DefaultZone", UNSET)

        default_policy = d.pop("DefaultPolicy", UNSET)

        batch_volumes_plan_body = cls(
            volumes=volumes,
            capacity_group=capacity_group,
            default_zone=default_zone,
            default_policy=default_policy,
        )

        batch_volumes_plan_body.additional_properties = d
        return batch_volumes_plan_body

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
