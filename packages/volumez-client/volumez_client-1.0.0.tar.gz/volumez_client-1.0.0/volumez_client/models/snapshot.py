from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.snapshot_consistency import SnapshotConsistency
from ..types import UNSET, Unset

T = TypeVar("T", bound="Snapshot")


@_attrs_define
class Snapshot:
    """
    Attributes:
        name (str):
        consistency (SnapshotConsistency):
        volumename (Union[Unset, str]):  Example: vol1.
        volumeid (Union[Unset, str]):
        volumesize (Union[Unset, int]):
        snapshotid (Union[Unset, str]):
        targetsecret (Union[Unset, str]):
        time (Union[Unset, str]):
        policy (Union[Unset, bool]):
        consistencygroup (Union[Unset, bool]):
        consistencygroupname (Union[Unset, str]):
        used (Union[Unset, int]):
        state (Union[Unset, str]):
        status (Union[Unset, str]):
        progress (Union[Unset, int]):
        numberofattachments (Union[Unset, int]):
    """

    name: str
    consistency: SnapshotConsistency
    volumename: Union[Unset, str] = UNSET
    volumeid: Union[Unset, str] = UNSET
    volumesize: Union[Unset, int] = UNSET
    snapshotid: Union[Unset, str] = UNSET
    targetsecret: Union[Unset, str] = UNSET
    time: Union[Unset, str] = UNSET
    policy: Union[Unset, bool] = UNSET
    consistencygroup: Union[Unset, bool] = UNSET
    consistencygroupname: Union[Unset, str] = UNSET
    used: Union[Unset, int] = UNSET
    state: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    progress: Union[Unset, int] = UNSET
    numberofattachments: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        consistency = self.consistency.value

        volumename = self.volumename

        volumeid = self.volumeid

        volumesize = self.volumesize

        snapshotid = self.snapshotid

        targetsecret = self.targetsecret

        time = self.time

        policy = self.policy

        consistencygroup = self.consistencygroup

        consistencygroupname = self.consistencygroupname

        used = self.used

        state = self.state

        status = self.status

        progress = self.progress

        numberofattachments = self.numberofattachments

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "consistency": consistency,
            }
        )
        if volumename is not UNSET:
            field_dict["volumename"] = volumename
        if volumeid is not UNSET:
            field_dict["volumeid"] = volumeid
        if volumesize is not UNSET:
            field_dict["volumesize"] = volumesize
        if snapshotid is not UNSET:
            field_dict["snapshotid"] = snapshotid
        if targetsecret is not UNSET:
            field_dict["targetsecret"] = targetsecret
        if time is not UNSET:
            field_dict["time"] = time
        if policy is not UNSET:
            field_dict["policy"] = policy
        if consistencygroup is not UNSET:
            field_dict["consistencygroup"] = consistencygroup
        if consistencygroupname is not UNSET:
            field_dict["consistencygroupname"] = consistencygroupname
        if used is not UNSET:
            field_dict["used"] = used
        if state is not UNSET:
            field_dict["state"] = state
        if status is not UNSET:
            field_dict["status"] = status
        if progress is not UNSET:
            field_dict["progress"] = progress
        if numberofattachments is not UNSET:
            field_dict["numberofattachments"] = numberofattachments

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        consistency = SnapshotConsistency(d.pop("consistency"))

        volumename = d.pop("volumename", UNSET)

        volumeid = d.pop("volumeid", UNSET)

        volumesize = d.pop("volumesize", UNSET)

        snapshotid = d.pop("snapshotid", UNSET)

        targetsecret = d.pop("targetsecret", UNSET)

        time = d.pop("time", UNSET)

        policy = d.pop("policy", UNSET)

        consistencygroup = d.pop("consistencygroup", UNSET)

        consistencygroupname = d.pop("consistencygroupname", UNSET)

        used = d.pop("used", UNSET)

        state = d.pop("state", UNSET)

        status = d.pop("status", UNSET)

        progress = d.pop("progress", UNSET)

        numberofattachments = d.pop("numberofattachments", UNSET)

        snapshot = cls(
            name=name,
            consistency=consistency,
            volumename=volumename,
            volumeid=volumeid,
            volumesize=volumesize,
            snapshotid=snapshotid,
            targetsecret=targetsecret,
            time=time,
            policy=policy,
            consistencygroup=consistencygroup,
            consistencygroupname=consistencygroupname,
            used=used,
            state=state,
            status=status,
            progress=progress,
            numberofattachments=numberofattachments,
        )

        snapshot.additional_properties = d
        return snapshot

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
