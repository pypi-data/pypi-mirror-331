from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.node_tags import NodeTags


T = TypeVar("T", bound="Node")


@_attrs_define
class Node:
    """
    Attributes:
        name (str):  Example: rv1.
        os (str):  Example: rhel.
        instanceid (Union[Unset, str]):
        osversion (Union[Unset, str]):  Example: 9.3.
        kversion (Union[Unset, str]):  Example: 6.5.13.
        controladdress (Union[Unset, str]):
        credential (Union[Unset, str]):
        account_id (Union[Unset, str]):
        region (Union[Unset, str]):  Example: us-east-1.
        zone (Union[Unset, str]):  Example: z1.
        resource_namespace (Union[Unset, str]): global namespace for resources in account empty if not
            aviliable/supported on cloud provider/node
        physical_proximity_group (Union[Unset, str]): identifier of the physical location of the node empty if not
            aviliable/supported on on cloud provider/node
        resiliency_domain (Union[Unset, str]): virtual domain for the node fault domains if aviliable/supported on on
            cloud provider/node
        fault_domain (Union[Unset, str]): identifier for node in FaultDomain
        offlinetime (Union[Unset, str]):
        state (Union[Unset, str]):
        status (Union[Unset, str]):
        progress (Union[Unset, int]):
        connectorversion (Union[Unset, str]):
        label (Union[Unset, str]):
        tags (Union[Unset, NodeTags]):
        cloudprovider (Union[Unset, str]):
        nodecluster (Union[Unset, str]):
        autoprovision_infra_uuid (Union[Unset, str]):
        instancetype (Union[Unset, str]):
    """

    name: str
    os: str
    instanceid: Union[Unset, str] = UNSET
    osversion: Union[Unset, str] = UNSET
    kversion: Union[Unset, str] = UNSET
    controladdress: Union[Unset, str] = UNSET
    credential: Union[Unset, str] = UNSET
    account_id: Union[Unset, str] = UNSET
    region: Union[Unset, str] = UNSET
    zone: Union[Unset, str] = UNSET
    resource_namespace: Union[Unset, str] = UNSET
    physical_proximity_group: Union[Unset, str] = UNSET
    resiliency_domain: Union[Unset, str] = UNSET
    fault_domain: Union[Unset, str] = UNSET
    offlinetime: Union[Unset, str] = UNSET
    state: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    progress: Union[Unset, int] = UNSET
    connectorversion: Union[Unset, str] = UNSET
    label: Union[Unset, str] = UNSET
    tags: Union[Unset, "NodeTags"] = UNSET
    cloudprovider: Union[Unset, str] = UNSET
    nodecluster: Union[Unset, str] = UNSET
    autoprovision_infra_uuid: Union[Unset, str] = UNSET
    instancetype: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        os = self.os

        instanceid = self.instanceid

        osversion = self.osversion

        kversion = self.kversion

        controladdress = self.controladdress

        credential = self.credential

        account_id = self.account_id

        region = self.region

        zone = self.zone

        resource_namespace = self.resource_namespace

        physical_proximity_group = self.physical_proximity_group

        resiliency_domain = self.resiliency_domain

        fault_domain = self.fault_domain

        offlinetime = self.offlinetime

        state = self.state

        status = self.status

        progress = self.progress

        connectorversion = self.connectorversion

        label = self.label

        tags: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags.to_dict()

        cloudprovider = self.cloudprovider

        nodecluster = self.nodecluster

        autoprovision_infra_uuid = self.autoprovision_infra_uuid

        instancetype = self.instancetype

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "os": os,
            }
        )
        if instanceid is not UNSET:
            field_dict["instanceid"] = instanceid
        if osversion is not UNSET:
            field_dict["osversion"] = osversion
        if kversion is not UNSET:
            field_dict["kversion"] = kversion
        if controladdress is not UNSET:
            field_dict["controladdress"] = controladdress
        if credential is not UNSET:
            field_dict["credential"] = credential
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
        if offlinetime is not UNSET:
            field_dict["offlinetime"] = offlinetime
        if state is not UNSET:
            field_dict["state"] = state
        if status is not UNSET:
            field_dict["status"] = status
        if progress is not UNSET:
            field_dict["progress"] = progress
        if connectorversion is not UNSET:
            field_dict["connectorversion"] = connectorversion
        if label is not UNSET:
            field_dict["label"] = label
        if tags is not UNSET:
            field_dict["tags"] = tags
        if cloudprovider is not UNSET:
            field_dict["cloudprovider"] = cloudprovider
        if nodecluster is not UNSET:
            field_dict["nodecluster"] = nodecluster
        if autoprovision_infra_uuid is not UNSET:
            field_dict["autoprovisionInfraUUID"] = autoprovision_infra_uuid
        if instancetype is not UNSET:
            field_dict["instancetype"] = instancetype

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.node_tags import NodeTags

        d = src_dict.copy()
        name = d.pop("name")

        os = d.pop("os")

        instanceid = d.pop("instanceid", UNSET)

        osversion = d.pop("osversion", UNSET)

        kversion = d.pop("kversion", UNSET)

        controladdress = d.pop("controladdress", UNSET)

        credential = d.pop("credential", UNSET)

        account_id = d.pop("accountID", UNSET)

        region = d.pop("region", UNSET)

        zone = d.pop("zone", UNSET)

        resource_namespace = d.pop("ResourceNamespace", UNSET)

        physical_proximity_group = d.pop("PhysicalProximityGroup", UNSET)

        resiliency_domain = d.pop("ResiliencyDomain", UNSET)

        fault_domain = d.pop("FaultDomain", UNSET)

        offlinetime = d.pop("offlinetime", UNSET)

        state = d.pop("state", UNSET)

        status = d.pop("status", UNSET)

        progress = d.pop("progress", UNSET)

        connectorversion = d.pop("connectorversion", UNSET)

        label = d.pop("label", UNSET)

        _tags = d.pop("tags", UNSET)
        tags: Union[Unset, NodeTags]
        if isinstance(_tags, Unset):
            tags = UNSET
        else:
            tags = NodeTags.from_dict(_tags)

        cloudprovider = d.pop("cloudprovider", UNSET)

        nodecluster = d.pop("nodecluster", UNSET)

        autoprovision_infra_uuid = d.pop("autoprovisionInfraUUID", UNSET)

        instancetype = d.pop("instancetype", UNSET)

        node = cls(
            name=name,
            os=os,
            instanceid=instanceid,
            osversion=osversion,
            kversion=kversion,
            controladdress=controladdress,
            credential=credential,
            account_id=account_id,
            region=region,
            zone=zone,
            resource_namespace=resource_namespace,
            physical_proximity_group=physical_proximity_group,
            resiliency_domain=resiliency_domain,
            fault_domain=fault_domain,
            offlinetime=offlinetime,
            state=state,
            status=status,
            progress=progress,
            connectorversion=connectorversion,
            label=label,
            tags=tags,
            cloudprovider=cloudprovider,
            nodecluster=nodecluster,
            autoprovision_infra_uuid=autoprovision_infra_uuid,
            instancetype=instancetype,
        )

        node.additional_properties = d
        return node

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
