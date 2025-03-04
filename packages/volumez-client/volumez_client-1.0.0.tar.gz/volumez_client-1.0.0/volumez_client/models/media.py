from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Media")


@_attrs_define
class Media:
    """
    Attributes:
        mediaid (Union[Unset, str]):
        size (Union[Unset, int]):
        model (Union[Unset, str]):
        media (Union[Unset, str]):
        bus (Union[Unset, str]):
        location (Union[Unset, str]):
        sed (Union[Unset, bool]):
        node (Union[Unset, str]):
        cloudprovider (Union[Unset, str]):
        account_id (Union[Unset, str]): the media node ResourceNamespace
        region (Union[Unset, str]):  Example: us-east-1.
        zone (Union[Unset, str]):
        resource_namespace (Union[Unset, str]): the media node ResourceNamespace
        physical_proximity_group (Union[Unset, str]): the media node PhysicalProximityGroup
        resiliency_domain (Union[Unset, str]): the media node ResiliencyDomain
        fault_domain (Union[Unset, str]): the media node FaultDomain
        firmware (Union[Unset, str]):
        sectorsize (Union[Unset, int]):
        iopsread (Union[Unset, int]):
        iopswrite (Union[Unset, int]):
        bandwidthread (Union[Unset, int]):
        bandwidthwrite (Union[Unset, int]):
        bandwidth_reserved (Union[Unset, int]):
        latencyread (Union[Unset, int]):
        latencywrite (Union[Unset, int]):
        offlinetime (Union[Unset, str]):
        freesize (Union[Unset, int]):
        freeiopsread (Union[Unset, int]):
        freeiopswrite (Union[Unset, int]):
        freebandwidthread (Union[Unset, int]):
        freebandwidthwrite (Union[Unset, int]):
        volumescount (Union[Unset, int]): count of how many volumes are using the media
        assignment (Union[Unset, str]):
        state (Union[Unset, str]):
        status (Union[Unset, str]):
        progress (Union[Unset, int]):
        capacitygroup (Union[Unset, str]): the capacity group this media belongs to
        lbaformats (Union[Unset, list[str]]): Available LBA formats for the media — ensure the block size specified in
            the media assignment matches one of these formats
    """

    mediaid: Union[Unset, str] = UNSET
    size: Union[Unset, int] = UNSET
    model: Union[Unset, str] = UNSET
    media: Union[Unset, str] = UNSET
    bus: Union[Unset, str] = UNSET
    location: Union[Unset, str] = UNSET
    sed: Union[Unset, bool] = UNSET
    node: Union[Unset, str] = UNSET
    cloudprovider: Union[Unset, str] = UNSET
    account_id: Union[Unset, str] = UNSET
    region: Union[Unset, str] = UNSET
    zone: Union[Unset, str] = UNSET
    resource_namespace: Union[Unset, str] = UNSET
    physical_proximity_group: Union[Unset, str] = UNSET
    resiliency_domain: Union[Unset, str] = UNSET
    fault_domain: Union[Unset, str] = UNSET
    firmware: Union[Unset, str] = UNSET
    sectorsize: Union[Unset, int] = UNSET
    iopsread: Union[Unset, int] = UNSET
    iopswrite: Union[Unset, int] = UNSET
    bandwidthread: Union[Unset, int] = UNSET
    bandwidthwrite: Union[Unset, int] = UNSET
    bandwidth_reserved: Union[Unset, int] = UNSET
    latencyread: Union[Unset, int] = UNSET
    latencywrite: Union[Unset, int] = UNSET
    offlinetime: Union[Unset, str] = UNSET
    freesize: Union[Unset, int] = UNSET
    freeiopsread: Union[Unset, int] = UNSET
    freeiopswrite: Union[Unset, int] = UNSET
    freebandwidthread: Union[Unset, int] = UNSET
    freebandwidthwrite: Union[Unset, int] = UNSET
    volumescount: Union[Unset, int] = UNSET
    assignment: Union[Unset, str] = UNSET
    state: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    progress: Union[Unset, int] = UNSET
    capacitygroup: Union[Unset, str] = UNSET
    lbaformats: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        mediaid = self.mediaid

        size = self.size

        model = self.model

        media = self.media

        bus = self.bus

        location = self.location

        sed = self.sed

        node = self.node

        cloudprovider = self.cloudprovider

        account_id = self.account_id

        region = self.region

        zone = self.zone

        resource_namespace = self.resource_namespace

        physical_proximity_group = self.physical_proximity_group

        resiliency_domain = self.resiliency_domain

        fault_domain = self.fault_domain

        firmware = self.firmware

        sectorsize = self.sectorsize

        iopsread = self.iopsread

        iopswrite = self.iopswrite

        bandwidthread = self.bandwidthread

        bandwidthwrite = self.bandwidthwrite

        bandwidth_reserved = self.bandwidth_reserved

        latencyread = self.latencyread

        latencywrite = self.latencywrite

        offlinetime = self.offlinetime

        freesize = self.freesize

        freeiopsread = self.freeiopsread

        freeiopswrite = self.freeiopswrite

        freebandwidthread = self.freebandwidthread

        freebandwidthwrite = self.freebandwidthwrite

        volumescount = self.volumescount

        assignment = self.assignment

        state = self.state

        status = self.status

        progress = self.progress

        capacitygroup = self.capacitygroup

        lbaformats: Union[Unset, list[str]] = UNSET
        if not isinstance(self.lbaformats, Unset):
            lbaformats = self.lbaformats

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if mediaid is not UNSET:
            field_dict["mediaid"] = mediaid
        if size is not UNSET:
            field_dict["size"] = size
        if model is not UNSET:
            field_dict["model"] = model
        if media is not UNSET:
            field_dict["media"] = media
        if bus is not UNSET:
            field_dict["bus"] = bus
        if location is not UNSET:
            field_dict["location"] = location
        if sed is not UNSET:
            field_dict["sed"] = sed
        if node is not UNSET:
            field_dict["node"] = node
        if cloudprovider is not UNSET:
            field_dict["cloudprovider"] = cloudprovider
        if account_id is not UNSET:
            field_dict["accountID"] = account_id
        if region is not UNSET:
            field_dict["region"] = region
        if zone is not UNSET:
            field_dict["zone"] = zone
        if resource_namespace is not UNSET:
            field_dict["ResourceNamespace"] = resource_namespace
        if physical_proximity_group is not UNSET:
            field_dict["PhysicalProximityGroup"] = physical_proximity_group
        if resiliency_domain is not UNSET:
            field_dict["ResiliencyDomain"] = resiliency_domain
        if fault_domain is not UNSET:
            field_dict["FaultDomain"] = fault_domain
        if firmware is not UNSET:
            field_dict["firmware"] = firmware
        if sectorsize is not UNSET:
            field_dict["sectorsize"] = sectorsize
        if iopsread is not UNSET:
            field_dict["iopsread"] = iopsread
        if iopswrite is not UNSET:
            field_dict["iopswrite"] = iopswrite
        if bandwidthread is not UNSET:
            field_dict["bandwidthread"] = bandwidthread
        if bandwidthwrite is not UNSET:
            field_dict["bandwidthwrite"] = bandwidthwrite
        if bandwidth_reserved is not UNSET:
            field_dict["BandwidthReserved"] = bandwidth_reserved
        if latencyread is not UNSET:
            field_dict["latencyread"] = latencyread
        if latencywrite is not UNSET:
            field_dict["latencywrite"] = latencywrite
        if offlinetime is not UNSET:
            field_dict["offlinetime"] = offlinetime
        if freesize is not UNSET:
            field_dict["freesize"] = freesize
        if freeiopsread is not UNSET:
            field_dict["freeiopsread"] = freeiopsread
        if freeiopswrite is not UNSET:
            field_dict["freeiopswrite"] = freeiopswrite
        if freebandwidthread is not UNSET:
            field_dict["freebandwidthread"] = freebandwidthread
        if freebandwidthwrite is not UNSET:
            field_dict["freebandwidthwrite"] = freebandwidthwrite
        if volumescount is not UNSET:
            field_dict["volumescount"] = volumescount
        if assignment is not UNSET:
            field_dict["assignment"] = assignment
        if state is not UNSET:
            field_dict["state"] = state
        if status is not UNSET:
            field_dict["status"] = status
        if progress is not UNSET:
            field_dict["progress"] = progress
        if capacitygroup is not UNSET:
            field_dict["capacitygroup"] = capacitygroup
        if lbaformats is not UNSET:
            field_dict["lbaformats"] = lbaformats

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        mediaid = d.pop("mediaid", UNSET)

        size = d.pop("size", UNSET)

        model = d.pop("model", UNSET)

        media = d.pop("media", UNSET)

        bus = d.pop("bus", UNSET)

        location = d.pop("location", UNSET)

        sed = d.pop("sed", UNSET)

        node = d.pop("node", UNSET)

        cloudprovider = d.pop("cloudprovider", UNSET)

        account_id = d.pop("accountID", UNSET)

        region = d.pop("region", UNSET)

        zone = d.pop("zone", UNSET)

        resource_namespace = d.pop("ResourceNamespace", UNSET)

        physical_proximity_group = d.pop("PhysicalProximityGroup", UNSET)

        resiliency_domain = d.pop("ResiliencyDomain", UNSET)

        fault_domain = d.pop("FaultDomain", UNSET)

        firmware = d.pop("firmware", UNSET)

        sectorsize = d.pop("sectorsize", UNSET)

        iopsread = d.pop("iopsread", UNSET)

        iopswrite = d.pop("iopswrite", UNSET)

        bandwidthread = d.pop("bandwidthread", UNSET)

        bandwidthwrite = d.pop("bandwidthwrite", UNSET)

        bandwidth_reserved = d.pop("BandwidthReserved", UNSET)

        latencyread = d.pop("latencyread", UNSET)

        latencywrite = d.pop("latencywrite", UNSET)

        offlinetime = d.pop("offlinetime", UNSET)

        freesize = d.pop("freesize", UNSET)

        freeiopsread = d.pop("freeiopsread", UNSET)

        freeiopswrite = d.pop("freeiopswrite", UNSET)

        freebandwidthread = d.pop("freebandwidthread", UNSET)

        freebandwidthwrite = d.pop("freebandwidthwrite", UNSET)

        volumescount = d.pop("volumescount", UNSET)

        assignment = d.pop("assignment", UNSET)

        state = d.pop("state", UNSET)

        status = d.pop("status", UNSET)

        progress = d.pop("progress", UNSET)

        capacitygroup = d.pop("capacitygroup", UNSET)

        lbaformats = cast(list[str], d.pop("lbaformats", UNSET))

        media = cls(
            mediaid=mediaid,
            size=size,
            model=model,
            media=media,
            bus=bus,
            location=location,
            sed=sed,
            node=node,
            cloudprovider=cloudprovider,
            account_id=account_id,
            region=region,
            zone=zone,
            resource_namespace=resource_namespace,
            physical_proximity_group=physical_proximity_group,
            resiliency_domain=resiliency_domain,
            fault_domain=fault_domain,
            firmware=firmware,
            sectorsize=sectorsize,
            iopsread=iopsread,
            iopswrite=iopswrite,
            bandwidthread=bandwidthread,
            bandwidthwrite=bandwidthwrite,
            bandwidth_reserved=bandwidth_reserved,
            latencyread=latencyread,
            latencywrite=latencywrite,
            offlinetime=offlinetime,
            freesize=freesize,
            freeiopsread=freeiopsread,
            freeiopswrite=freeiopswrite,
            freebandwidthread=freebandwidthread,
            freebandwidthwrite=freebandwidthwrite,
            volumescount=volumescount,
            assignment=assignment,
            state=state,
            status=status,
            progress=progress,
            capacitygroup=capacitygroup,
            lbaformats=lbaformats,
        )

        media.additional_properties = d
        return media

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
