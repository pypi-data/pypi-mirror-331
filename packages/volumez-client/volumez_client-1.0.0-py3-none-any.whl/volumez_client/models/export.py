from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.export_create import ExportCreate
    from ..models.storage_port import StoragePort


T = TypeVar("T", bound="Export")


@_attrs_define
class Export:
    """
    Attributes:
        id (Union[Unset, str]):
        params (Union[Unset, ExportCreate]):
        volumename (Union[Unset, str]):  Example: vol1.
        snapshotname (Union[Unset, str]):
        state (Union[Unset, str]):
        status (Union[Unset, str]):
        progress (Union[Unset, int]):
        xqn (Union[Unset, str]):
        wwn (Union[Unset, str]):
        ports (Union[Unset, list['StoragePort']]):
    """

    id: Union[Unset, str] = UNSET
    params: Union[Unset, "ExportCreate"] = UNSET
    volumename: Union[Unset, str] = UNSET
    snapshotname: Union[Unset, str] = UNSET
    state: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    progress: Union[Unset, int] = UNSET
    xqn: Union[Unset, str] = UNSET
    wwn: Union[Unset, str] = UNSET
    ports: Union[Unset, list["StoragePort"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        params: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.params, Unset):
            params = self.params.to_dict()

        volumename = self.volumename

        snapshotname = self.snapshotname

        state = self.state

        status = self.status

        progress = self.progress

        xqn = self.xqn

        wwn = self.wwn

        ports: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.ports, Unset):
            ports = []
            for ports_item_data in self.ports:
                ports_item = ports_item_data.to_dict()
                ports.append(ports_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if params is not UNSET:
            field_dict["params"] = params
        if volumename is not UNSET:
            field_dict["volumename"] = volumename
        if snapshotname is not UNSET:
            field_dict["snapshotname"] = snapshotname
        if state is not UNSET:
            field_dict["state"] = state
        if status is not UNSET:
            field_dict["status"] = status
        if progress is not UNSET:
            field_dict["progress"] = progress
        if xqn is not UNSET:
            field_dict["xqn"] = xqn
        if wwn is not UNSET:
            field_dict["wwn"] = wwn
        if ports is not UNSET:
            field_dict["ports"] = ports

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.export_create import ExportCreate
        from ..models.storage_port import StoragePort

        d = src_dict.copy()
        id = d.pop("id", UNSET)

        _params = d.pop("params", UNSET)
        params: Union[Unset, ExportCreate]
        if isinstance(_params, Unset):
            params = UNSET
        else:
            params = ExportCreate.from_dict(_params)

        volumename = d.pop("volumename", UNSET)

        snapshotname = d.pop("snapshotname", UNSET)

        state = d.pop("state", UNSET)

        status = d.pop("status", UNSET)

        progress = d.pop("progress", UNSET)

        xqn = d.pop("xqn", UNSET)

        wwn = d.pop("wwn", UNSET)

        ports = []
        _ports = d.pop("ports", UNSET)
        for ports_item_data in _ports or []:
            ports_item = StoragePort.from_dict(ports_item_data)

            ports.append(ports_item)

        export = cls(
            id=id,
            params=params,
            volumename=volumename,
            snapshotname=snapshotname,
            state=state,
            status=status,
            progress=progress,
            xqn=xqn,
            wwn=wwn,
            ports=ports,
        )

        export.additional_properties = d
        return export

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
