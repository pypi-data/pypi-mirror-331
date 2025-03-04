from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.node_describe_response_volumes_map import NodeDescribeResponseVolumesMap


T = TypeVar("T", bound="NodeDescribeResponse")


@_attrs_define
class NodeDescribeResponse:
    """
    Attributes:
        volumes_map (Union[Unset, NodeDescribeResponseVolumesMap]): Map of volume IDs to volume objects
    """

    volumes_map: Union[Unset, "NodeDescribeResponseVolumesMap"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        volumes_map: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.volumes_map, Unset):
            volumes_map = self.volumes_map.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if volumes_map is not UNSET:
            field_dict["volumesMap"] = volumes_map

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.node_describe_response_volumes_map import NodeDescribeResponseVolumesMap

        d = src_dict.copy()
        _volumes_map = d.pop("volumesMap", UNSET)
        volumes_map: Union[Unset, NodeDescribeResponseVolumesMap]
        if isinstance(_volumes_map, Unset):
            volumes_map = UNSET
        else:
            volumes_map = NodeDescribeResponseVolumesMap.from_dict(_volumes_map)

        node_describe_response = cls(
            volumes_map=volumes_map,
        )

        node_describe_response.additional_properties = d
        return node_describe_response

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
