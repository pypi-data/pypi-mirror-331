from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.consistency_group_snapshot_create_body_consistency import ConsistencyGroupSnapshotCreateBodyConsistency
from ..types import UNSET, Unset

T = TypeVar("T", bound="ConsistencyGroupSnapshotCreateBody")


@_attrs_define
class ConsistencyGroupSnapshotCreateBody:
    """
    Attributes:
        name (Union[Unset, str]):
        consistency (Union[Unset, ConsistencyGroupSnapshotCreateBodyConsistency]):
        group_name (Union[Unset, str]):
        volumes (Union[Unset, list[str]]):
    """

    name: Union[Unset, str] = UNSET
    consistency: Union[Unset, ConsistencyGroupSnapshotCreateBodyConsistency] = UNSET
    group_name: Union[Unset, str] = UNSET
    volumes: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        consistency: Union[Unset, str] = UNSET
        if not isinstance(self.consistency, Unset):
            consistency = self.consistency.value

        group_name = self.group_name

        volumes: Union[Unset, list[str]] = UNSET
        if not isinstance(self.volumes, Unset):
            volumes = self.volumes

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if consistency is not UNSET:
            field_dict["consistency"] = consistency
        if group_name is not UNSET:
            field_dict["group_name"] = group_name
        if volumes is not UNSET:
            field_dict["volumes"] = volumes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name", UNSET)

        _consistency = d.pop("consistency", UNSET)
        consistency: Union[Unset, ConsistencyGroupSnapshotCreateBodyConsistency]
        if isinstance(_consistency, Unset):
            consistency = UNSET
        else:
            consistency = ConsistencyGroupSnapshotCreateBodyConsistency(_consistency)

        group_name = d.pop("group_name", UNSET)

        volumes = cast(list[str], d.pop("volumes", UNSET))

        consistency_group_snapshot_create_body = cls(
            name=name,
            consistency=consistency,
            group_name=group_name,
            volumes=volumes,
        )

        consistency_group_snapshot_create_body.additional_properties = d
        return consistency_group_snapshot_create_body

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
