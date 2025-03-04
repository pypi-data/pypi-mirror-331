from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.volume_group import VolumeGroup


T = TypeVar("T", bound="Plan")


@_attrs_define
class Plan:
    """
    Attributes:
        volumegroup (VolumeGroup):
        replicationvolumegroup (Union[Unset, VolumeGroup]):
    """

    volumegroup: "VolumeGroup"
    replicationvolumegroup: Union[Unset, "VolumeGroup"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        volumegroup = self.volumegroup.to_dict()

        replicationvolumegroup: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.replicationvolumegroup, Unset):
            replicationvolumegroup = self.replicationvolumegroup.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "volumegroup": volumegroup,
            }
        )
        if replicationvolumegroup is not UNSET:
            field_dict["replicationvolumegroup"] = replicationvolumegroup

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.volume_group import VolumeGroup

        d = src_dict.copy()
        volumegroup = VolumeGroup.from_dict(d.pop("volumegroup"))

        _replicationvolumegroup = d.pop("replicationvolumegroup", UNSET)
        replicationvolumegroup: Union[Unset, VolumeGroup]
        if isinstance(_replicationvolumegroup, Unset):
            replicationvolumegroup = UNSET
        else:
            replicationvolumegroup = VolumeGroup.from_dict(_replicationvolumegroup)

        plan = cls(
            volumegroup=volumegroup,
            replicationvolumegroup=replicationvolumegroup,
        )

        plan.additional_properties = d
        return plan

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
