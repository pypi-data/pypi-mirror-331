from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Attachment")


@_attrs_define
class Attachment:
    """
    Attributes:
        node (str):
        volumename (Union[Unset, str]):  Example: vol1.
        volumeid (Union[Unset, str]):
        snapshotname (Union[Unset, str]):
        snapshotid (Union[Unset, str]):
        state (Union[Unset, str]):
        status (Union[Unset, str]):
        progress (Union[Unset, int]):
        mountpoint (Union[Unset, str]):
        readonly (Union[Unset, bool]):
        allocated_resources (Union[Unset, int]):
    """

    node: str
    volumename: Union[Unset, str] = UNSET
    volumeid: Union[Unset, str] = UNSET
    snapshotname: Union[Unset, str] = UNSET
    snapshotid: Union[Unset, str] = UNSET
    state: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    progress: Union[Unset, int] = UNSET
    mountpoint: Union[Unset, str] = UNSET
    readonly: Union[Unset, bool] = UNSET
    allocated_resources: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        node = self.node

        volumename = self.volumename

        volumeid = self.volumeid

        snapshotname = self.snapshotname

        snapshotid = self.snapshotid

        state = self.state

        status = self.status

        progress = self.progress

        mountpoint = self.mountpoint

        readonly = self.readonly

        allocated_resources = self.allocated_resources

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "node": node,
            }
        )
        if volumename is not UNSET:
            field_dict["volumename"] = volumename
        if volumeid is not UNSET:
            field_dict["volumeid"] = volumeid
        if snapshotname is not UNSET:
            field_dict["snapshotname"] = snapshotname
        if snapshotid is not UNSET:
            field_dict["snapshotid"] = snapshotid
        if state is not UNSET:
            field_dict["state"] = state
        if status is not UNSET:
            field_dict["status"] = status
        if progress is not UNSET:
            field_dict["progress"] = progress
        if mountpoint is not UNSET:
            field_dict["mountpoint"] = mountpoint
        if readonly is not UNSET:
            field_dict["readonly"] = readonly
        if allocated_resources is not UNSET:
            field_dict["allocated_resources"] = allocated_resources

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        node = d.pop("node")

        volumename = d.pop("volumename", UNSET)

        volumeid = d.pop("volumeid", UNSET)

        snapshotname = d.pop("snapshotname", UNSET)

        snapshotid = d.pop("snapshotid", UNSET)

        state = d.pop("state", UNSET)

        status = d.pop("status", UNSET)

        progress = d.pop("progress", UNSET)

        mountpoint = d.pop("mountpoint", UNSET)

        readonly = d.pop("readonly", UNSET)

        allocated_resources = d.pop("allocated_resources", UNSET)

        attachment = cls(
            node=node,
            volumename=volumename,
            volumeid=volumeid,
            snapshotname=snapshotname,
            snapshotid=snapshotid,
            state=state,
            status=status,
            progress=progress,
            mountpoint=mountpoint,
            readonly=readonly,
            allocated_resources=allocated_resources,
        )

        attachment.additional_properties = d
        return attachment

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
