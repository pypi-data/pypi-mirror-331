from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.volume_flavor import VolumeFlavor
from ..models.volume_type import VolumeType
from ..types import UNSET, Unset

T = TypeVar("T", bound="Volume")


@_attrs_define
class Volume:
    """
    Attributes:
        name (str):  Example: vol1.
        type_ (VolumeType):
        size (int):  Example: 10.
        policy (str):
        volumeid (Union[Unset, str]):
        contentvolume (Union[Unset, str]):
        contentsnapshot (Union[Unset, str]):
        maxsize (Union[Unset, int]):  Example: 100.
        consistencygroup (Union[Unset, str]):
        node (Union[Unset, str]):
        zone (Union[Unset, str]):  Example: eu-west-2.
        zonereplica (Union[Unset, str]):
        volumegroupname (Union[Unset, str]):  Example: vg_1.
        volumegroupid (Union[Unset, str]):
        replicationnode (Union[Unset, str]):
        replicationvolumegroupname (Union[Unset, str]):  Example: vg_1.
        replicationvolumegroupid (Union[Unset, str]):
        volumerecoveryjob (Union[Unset, str]):
        state (Union[Unset, str]):
        status (Union[Unset, str]):
        progress (Union[Unset, int]):
        capacitygroup (Union[Unset, str]):
        throttlingscheme (Union[Unset, str]):
        allowdatamovement (Union[Unset, bool]):  Default: False.
        flavor (Union[Unset, VolumeFlavor]):
    """

    name: str
    type_: VolumeType
    size: int
    policy: str
    volumeid: Union[Unset, str] = UNSET
    contentvolume: Union[Unset, str] = UNSET
    contentsnapshot: Union[Unset, str] = UNSET
    maxsize: Union[Unset, int] = UNSET
    consistencygroup: Union[Unset, str] = UNSET
    node: Union[Unset, str] = UNSET
    zone: Union[Unset, str] = UNSET
    zonereplica: Union[Unset, str] = UNSET
    volumegroupname: Union[Unset, str] = UNSET
    volumegroupid: Union[Unset, str] = UNSET
    replicationnode: Union[Unset, str] = UNSET
    replicationvolumegroupname: Union[Unset, str] = UNSET
    replicationvolumegroupid: Union[Unset, str] = UNSET
    volumerecoveryjob: Union[Unset, str] = UNSET
    state: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    progress: Union[Unset, int] = UNSET
    capacitygroup: Union[Unset, str] = UNSET
    throttlingscheme: Union[Unset, str] = UNSET
    allowdatamovement: Union[Unset, bool] = False
    flavor: Union[Unset, VolumeFlavor] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        type_ = self.type_.value

        size = self.size

        policy = self.policy

        volumeid = self.volumeid

        contentvolume = self.contentvolume

        contentsnapshot = self.contentsnapshot

        maxsize = self.maxsize

        consistencygroup = self.consistencygroup

        node = self.node

        zone = self.zone

        zonereplica = self.zonereplica

        volumegroupname = self.volumegroupname

        volumegroupid = self.volumegroupid

        replicationnode = self.replicationnode

        replicationvolumegroupname = self.replicationvolumegroupname

        replicationvolumegroupid = self.replicationvolumegroupid

        volumerecoveryjob = self.volumerecoveryjob

        state = self.state

        status = self.status

        progress = self.progress

        capacitygroup = self.capacitygroup

        throttlingscheme = self.throttlingscheme

        allowdatamovement = self.allowdatamovement

        flavor: Union[Unset, str] = UNSET
        if not isinstance(self.flavor, Unset):
            flavor = self.flavor.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "type": type_,
                "size": size,
                "policy": policy,
            }
        )
        if volumeid is not UNSET:
            field_dict["volumeid"] = volumeid
        if contentvolume is not UNSET:
            field_dict["contentvolume"] = contentvolume
        if contentsnapshot is not UNSET:
            field_dict["contentsnapshot"] = contentsnapshot
        if maxsize is not UNSET:
            field_dict["maxsize"] = maxsize
        if consistencygroup is not UNSET:
            field_dict["consistencygroup"] = consistencygroup
        if node is not UNSET:
            field_dict["node"] = node
        if zone is not UNSET:
            field_dict["zone"] = zone
        if zonereplica is not UNSET:
            field_dict["zonereplica"] = zonereplica
        if volumegroupname is not UNSET:
            field_dict["volumegroupname"] = volumegroupname
        if volumegroupid is not UNSET:
            field_dict["volumegroupid"] = volumegroupid
        if replicationnode is not UNSET:
            field_dict["replicationnode"] = replicationnode
        if replicationvolumegroupname is not UNSET:
            field_dict["replicationvolumegroupname"] = replicationvolumegroupname
        if replicationvolumegroupid is not UNSET:
            field_dict["replicationvolumegroupid"] = replicationvolumegroupid
        if volumerecoveryjob is not UNSET:
            field_dict["volumerecoveryjob"] = volumerecoveryjob
        if state is not UNSET:
            field_dict["state"] = state
        if status is not UNSET:
            field_dict["status"] = status
        if progress is not UNSET:
            field_dict["progress"] = progress
        if capacitygroup is not UNSET:
            field_dict["capacitygroup"] = capacitygroup
        if throttlingscheme is not UNSET:
            field_dict["throttlingscheme"] = throttlingscheme
        if allowdatamovement is not UNSET:
            field_dict["allowdatamovement"] = allowdatamovement
        if flavor is not UNSET:
            field_dict["flavor"] = flavor

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        type_ = VolumeType(d.pop("type"))

        size = d.pop("size")

        policy = d.pop("policy")

        volumeid = d.pop("volumeid", UNSET)

        contentvolume = d.pop("contentvolume", UNSET)

        contentsnapshot = d.pop("contentsnapshot", UNSET)

        maxsize = d.pop("maxsize", UNSET)

        consistencygroup = d.pop("consistencygroup", UNSET)

        node = d.pop("node", UNSET)

        zone = d.pop("zone", UNSET)

        zonereplica = d.pop("zonereplica", UNSET)

        volumegroupname = d.pop("volumegroupname", UNSET)

        volumegroupid = d.pop("volumegroupid", UNSET)

        replicationnode = d.pop("replicationnode", UNSET)

        replicationvolumegroupname = d.pop("replicationvolumegroupname", UNSET)

        replicationvolumegroupid = d.pop("replicationvolumegroupid", UNSET)

        volumerecoveryjob = d.pop("volumerecoveryjob", UNSET)

        state = d.pop("state", UNSET)

        status = d.pop("status", UNSET)

        progress = d.pop("progress", UNSET)

        capacitygroup = d.pop("capacitygroup", UNSET)

        throttlingscheme = d.pop("throttlingscheme", UNSET)

        allowdatamovement = d.pop("allowdatamovement", UNSET)

        _flavor = d.pop("flavor", UNSET)
        flavor: Union[Unset, VolumeFlavor]
        if isinstance(_flavor, Unset):
            flavor = UNSET
        else:
            flavor = VolumeFlavor(_flavor)

        volume = cls(
            name=name,
            type_=type_,
            size=size,
            policy=policy,
            volumeid=volumeid,
            contentvolume=contentvolume,
            contentsnapshot=contentsnapshot,
            maxsize=maxsize,
            consistencygroup=consistencygroup,
            node=node,
            zone=zone,
            zonereplica=zonereplica,
            volumegroupname=volumegroupname,
            volumegroupid=volumegroupid,
            replicationnode=replicationnode,
            replicationvolumegroupname=replicationvolumegroupname,
            replicationvolumegroupid=replicationvolumegroupid,
            volumerecoveryjob=volumerecoveryjob,
            state=state,
            status=status,
            progress=progress,
            capacitygroup=capacitygroup,
            throttlingscheme=throttlingscheme,
            allowdatamovement=allowdatamovement,
            flavor=flavor,
        )

        volume.additional_properties = d
        return volume

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
