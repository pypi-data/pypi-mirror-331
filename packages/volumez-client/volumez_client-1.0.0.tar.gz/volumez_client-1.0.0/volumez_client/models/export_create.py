from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.authentication import Authentication
    from ..models.export_create_nodes_item import ExportCreateNodesItem


T = TypeVar("T", bound="ExportCreate")


@_attrs_define
class ExportCreate:
    """
    Attributes:
        target_name (Union[Unset, str]):
        protocol (Union[Unset, str]):
        authentication (Union[Unset, Authentication]):
        volumeid (Union[Unset, str]):
        snapshotid (Union[Unset, str]):
        allowed_hosts (Union[Unset, list[str]]):
        nodes (Union[Unset, list['ExportCreateNodesItem']]):
    """

    target_name: Union[Unset, str] = UNSET
    protocol: Union[Unset, str] = UNSET
    authentication: Union[Unset, "Authentication"] = UNSET
    volumeid: Union[Unset, str] = UNSET
    snapshotid: Union[Unset, str] = UNSET
    allowed_hosts: Union[Unset, list[str]] = UNSET
    nodes: Union[Unset, list["ExportCreateNodesItem"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        target_name = self.target_name

        protocol = self.protocol

        authentication: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.authentication, Unset):
            authentication = self.authentication.to_dict()

        volumeid = self.volumeid

        snapshotid = self.snapshotid

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
        if target_name is not UNSET:
            field_dict["target_name"] = target_name
        if protocol is not UNSET:
            field_dict["protocol"] = protocol
        if authentication is not UNSET:
            field_dict["authentication"] = authentication
        if volumeid is not UNSET:
            field_dict["volumeid"] = volumeid
        if snapshotid is not UNSET:
            field_dict["snapshotid"] = snapshotid
        if allowed_hosts is not UNSET:
            field_dict["allowed_hosts"] = allowed_hosts
        if nodes is not UNSET:
            field_dict["nodes"] = nodes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.authentication import Authentication
        from ..models.export_create_nodes_item import ExportCreateNodesItem

        d = src_dict.copy()
        target_name = d.pop("target_name", UNSET)

        protocol = d.pop("protocol", UNSET)

        _authentication = d.pop("authentication", UNSET)
        authentication: Union[Unset, Authentication]
        if isinstance(_authentication, Unset):
            authentication = UNSET
        else:
            authentication = Authentication.from_dict(_authentication)

        volumeid = d.pop("volumeid", UNSET)

        snapshotid = d.pop("snapshotid", UNSET)

        allowed_hosts = cast(list[str], d.pop("allowed_hosts", UNSET))

        nodes = []
        _nodes = d.pop("nodes", UNSET)
        for nodes_item_data in _nodes or []:
            nodes_item = ExportCreateNodesItem.from_dict(nodes_item_data)

            nodes.append(nodes_item)

        export_create = cls(
            target_name=target_name,
            protocol=protocol,
            authentication=authentication,
            volumeid=volumeid,
            snapshotid=snapshotid,
            allowed_hosts=allowed_hosts,
            nodes=nodes,
        )

        export_create.additional_properties = d
        return export_create

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
