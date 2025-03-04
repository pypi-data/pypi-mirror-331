from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Association")


@_attrs_define
class Association:
    """
    Attributes:
        name (Union[Unset, str]):
        id (Union[Unset, str]):
        volumename (Union[Unset, str]):  Example: vol1.
        volumeid (Union[Unset, str]):
        snapshotname (Union[Unset, str]):
        snapshotid (Union[Unset, str]):
        state (Union[Unset, str]):
        status (Union[Unset, str]):
    """

    name: Union[Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    volumename: Union[Unset, str] = UNSET
    volumeid: Union[Unset, str] = UNSET
    snapshotname: Union[Unset, str] = UNSET
    snapshotid: Union[Unset, str] = UNSET
    state: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        id = self.id

        volumename = self.volumename

        volumeid = self.volumeid

        snapshotname = self.snapshotname

        snapshotid = self.snapshotid

        state = self.state

        status = self.status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if id is not UNSET:
            field_dict["id"] = id
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

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name", UNSET)

        id = d.pop("id", UNSET)

        volumename = d.pop("volumename", UNSET)

        volumeid = d.pop("volumeid", UNSET)

        snapshotname = d.pop("snapshotname", UNSET)

        snapshotid = d.pop("snapshotid", UNSET)

        state = d.pop("state", UNSET)

        status = d.pop("status", UNSET)

        association = cls(
            name=name,
            id=id,
            volumename=volumename,
            volumeid=volumeid,
            snapshotname=snapshotname,
            snapshotid=snapshotid,
            state=state,
            status=status,
        )

        association.additional_properties = d
        return association

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
