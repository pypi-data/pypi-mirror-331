from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.export_modify_nodes_item import ExportModifyNodesItem


T = TypeVar("T", bound="ExportModify")


@_attrs_define
class ExportModify:
    """
    Attributes:
        allowed_hosts (Union[Unset, list[str]]):
        nodes (Union[Unset, list['ExportModifyNodesItem']]):
    """

    allowed_hosts: Union[Unset, list[str]] = UNSET
    nodes: Union[Unset, list["ExportModifyNodesItem"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        allowed_hosts: Union[Unset, list[str]] = UNSET
        if not isinstance(self.allowed_hosts, Unset):
            allowed_hosts = self.allowed_hosts

        nodes: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.nodes, Unset):
            nodes = []
            for nodes_item_data in self.nodes:
                nodes_item = nodes_item_data.to_dict()
                nodes.append(nodes_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if allowed_hosts is not UNSET:
            field_dict["allowed_hosts"] = allowed_hosts
        if nodes is not UNSET:
            field_dict["nodes"] = nodes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.export_modify_nodes_item import ExportModifyNodesItem

        d = src_dict.copy()
        allowed_hosts = cast(list[str], d.pop("allowed_hosts", UNSET))

        nodes = []
        _nodes = d.pop("nodes", UNSET)
        for nodes_item_data in _nodes or []:
            nodes_item = ExportModifyNodesItem.from_dict(nodes_item_data)

            nodes.append(nodes_item)

        export_modify = cls(
            allowed_hosts=allowed_hosts,
            nodes=nodes,
        )

        export_modify.additional_properties = d
        return export_modify

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
