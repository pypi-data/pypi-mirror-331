from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.policy_capacityoptimization import PolicyCapacityoptimization
from ..types import UNSET, Unset

T = TypeVar("T", bound="Policy")


@_attrs_define
class Policy:
    """
    Attributes:
        name (str): A name for the policy. The name can be any non-empty string that does not contain a white space.
        capacityoptimization (PolicyCapacityoptimization): Choosing “Capacity” directs Volumez to prefer using capacity-
            saving methods (such as compression, deduplication, erasure coding and thin provisioning) where relevant, in
            order to consume the minimum amount of raw media. Using such methods might take some CPU cycles, and might
            reduce the performance of your volumes (it will still be within the range you specified). Choosing “Balanced”
            directs Volumez to prefer using some capacity-saving methods where relevant, in order to use less raw media,
            while consuming a small amount of CPU cycles. “Performance Optimized” directs Volumez to avoid using capacity-
            saving any methods (such as compression and deduplication) that reduce media consumption. This way applications
            can get the optimal performance from their media, however more raw media might be consumed to provision
            Performance-Optimized volumes.
        iopswrite (Union[Unset, int]): Enter the maximum write IOPS that a volume is expected to sustain (assuming 8K
            writes). Write IOPS should be a positive integer number. Volumez will guarantee to provide this performance,
            regardless of the volume size or other volumes. Example: 1000.
        iopsread (Union[Unset, int]): Enter the maximum read IOPS that a volume is expected to sustain (assuming 8K
            reads). Read IOPS should be a positive integer number. Volumez will guarantee to provide this performance,
            regardless of the volume size or other volumes. Example: 1000.
        bandwidthwrite (Union[Unset, int]): Enter the maximum write bandwidth that a volume is expected to sustain.
            Write Bandwidth should be a positive integer number. Volumez will guarantee to provide this performance,
            regardless of the volume size or other volumes.
        bandwidthread (Union[Unset, int]): Enter the maximum read bandwidth that a volume is expected to sustain. Read
            Bandwidth should be a positive integer number. Volumez will guarantee to provide this performance, regardless of
            the volume size or other volumes.
        latencywrite (Union[Unset, int]): Enter the maximum latency that a volume is expected to sustain. Write latency
            should be a positive integer number. Volumez will guarantee to provide this performance, regardless of the
            volume size or other volumes.
        latencyread (Union[Unset, int]): Enter the maximum read IOPS that a volume is expected to sustain. Read latency
            should be a positive integer number. Volumez will guarantee to provide this performance, regardless of the
            volume size or other volumes.
        latencyreadcold (Union[Unset, int]):  If not all the reads are hot (i.e., Percentage of Cold Reads is >0) –
            Enter the more relaxed constraints for read latencies of cold data.  Valid values: non-negative integer number,
            that is larger than “Read Latency”.
        colddata (Union[Unset, int]): Enter the percentage of the volume’s capacity that is expected to be “cold” (i.e.
            expected to only have infrequent reads). Default is 0%. Values that are greater than 0 give Volumez the option
            to use more economic media with more relaxed read performance requirements. Valid values: Integers in the range
            of 0..100.
        localzoneread (Union[Unset, bool]): Setting this value to “Yes” directs Volumez to prefer volume configurations
            where reads are usually happening from disks that are in the same zone as the application. This saves east-west
            network traffic across zones, however more media per zone will be required to achieve read-IOPs requirements.
            Set this value to “Yes” if you have network constraints (bandwidth or cost) across your zones; otherwise set it
            to “No”.
        failureperformance (Union[Unset, bool]): Setting this value to “Yes” directs Volumez to over-provision volumes
            in a way that even after having a failure, the volumes will have the desired performance. Setting this value to
            “No” directs Volumez to provision volumes according to the desired performance, however in a case of failure –
            performance may be impacted. The default value is “No”.
        capacityreservation (Union[Unset, int]): Enter how much logical capacity is reserved up-front for the
            applications to use. If more capacity is needed for the volume, it will be allocated based on availability of
            media. Capacities that are reserved can be used for the volume itself and for its snapshots. For example – Use
            0% for thin-provisioned volumes, 130% for thick-provisioned volumes with estimated 30% of space for snapshots.
            Valid values are 0%-500%, default is 20%. Example: 20.
        resiliencymedia (Union[Unset, int]):  Enter how many media failures (e.g. disk, memory card) the system is
            required to sustain, and still serve volumes of this policy. A value of “0” means any disk failure will result
            data unavailability and loss. Valid values are 0..3, default value is 2. Example: 2.
        resiliencynode (Union[Unset, int]): Enter how many Volumez node (e.g. EC2 instance, server) failures the system
            is required to sustain, and still serve volumes of this policy. This is different than “Media failures” because
            sometimes multiple media copies may end on a single node. A value of “0” means any node failure will result data
            unavailability and loss. Valid values are 0..3, default value is 1. Example: 1.
        resiliencyzone (Union[Unset, int]): Enter how many zones (e.g. AWS availability zones, DataCenters Buildings)
            failures the system is required to sustain, and still serve volumes of this policy. Note: zones are assumed to
            be within the same metro distance, and resiliency to zone failures means cross-zone network traffic. Valid
            values are 0..2, default value is 1. Example: 1.
        resiliencyregion (Union[Unset, int]): Enter how many regions (e.g. AWS regions zones, DataCenters across
            continents) failures the system is required to sustain, and still serve volumes of this policy. Note: regions
            are assumed to reside across WAN distance, with some bandwidth limitations. Valid values are 0 and 1, default
            value is 0. Example: 1.
        replicationrpo (Union[Unset, int]): Enter how many seconds are allowed for the replica to stay behind the
            primary storage. 0 means synchronous replication. Valid values are 0..3600, default value is 0. Max value: 3600.
            (1 hour).
        replicationbandwidth (Union[Unset, int]): Specifies the maximum bandwidth that Volumez is allowed to consume for
            replication of this volume (MB/s). 0 means no bandwidth limitation.
        encryption (Union[Unset, bool]): Enter “YES” to encrypt the data in server where the application is running.
            Note: No change is needed in the applications themselves, however encryption will consume some CPU cycles on the
            application server. Default value NO.
        sed (Union[Unset, bool]): Enter “YES” to direct Volumez to only use media with disk encryption capabilities.
            Note that specifying “NO” can still use such media, however it is not a must to use it. Default value: NO.
        integrity (Union[Unset, bool]): Enter “YES” to direct Volumez to activate the “Device Mapper integrity”
            protection for the volume. This capability provides strong integrity checking. Note: No change is needed in the
            applications themselves, however Data Integrity will consume non-negligible CPU cycles on the application
            server. Default value: NO.
        snapshotkeep (Union[Unset, int]):
        snapshotfrequency (Union[Unset, str]):
        snapshotday (Union[Unset, int]):
        snapshothour (Union[Unset, int]):
        snapshotminute (Union[Unset, int]):
        createdbyuser_name (Union[Unset, str]):
        createdbyuseremail (Union[Unset, str]):
        createdtime (Union[Unset, str]):
        updatebyusername (Union[Unset, str]):
        updateby_useremail (Union[Unset, str]):
        updatetime (Union[Unset, str]):
    """

    name: str
    capacityoptimization: PolicyCapacityoptimization
    iopswrite: Union[Unset, int] = UNSET
    iopsread: Union[Unset, int] = UNSET
    bandwidthwrite: Union[Unset, int] = UNSET
    bandwidthread: Union[Unset, int] = UNSET
    latencywrite: Union[Unset, int] = UNSET
    latencyread: Union[Unset, int] = UNSET
    latencyreadcold: Union[Unset, int] = UNSET
    colddata: Union[Unset, int] = UNSET
    localzoneread: Union[Unset, bool] = UNSET
    failureperformance: Union[Unset, bool] = UNSET
    capacityreservation: Union[Unset, int] = UNSET
    resiliencymedia: Union[Unset, int] = UNSET
    resiliencynode: Union[Unset, int] = UNSET
    resiliencyzone: Union[Unset, int] = UNSET
    resiliencyregion: Union[Unset, int] = UNSET
    replicationrpo: Union[Unset, int] = UNSET
    replicationbandwidth: Union[Unset, int] = UNSET
    encryption: Union[Unset, bool] = UNSET
    sed: Union[Unset, bool] = UNSET
    integrity: Union[Unset, bool] = UNSET
    snapshotkeep: Union[Unset, int] = UNSET
    snapshotfrequency: Union[Unset, str] = UNSET
    snapshotday: Union[Unset, int] = UNSET
    snapshothour: Union[Unset, int] = UNSET
    snapshotminute: Union[Unset, int] = UNSET
    createdbyuser_name: Union[Unset, str] = UNSET
    createdbyuseremail: Union[Unset, str] = UNSET
    createdtime: Union[Unset, str] = UNSET
    updatebyusername: Union[Unset, str] = UNSET
    updateby_useremail: Union[Unset, str] = UNSET
    updatetime: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        capacityoptimization = self.capacityoptimization.value

        iopswrite = self.iopswrite

        iopsread = self.iopsread

        bandwidthwrite = self.bandwidthwrite

        bandwidthread = self.bandwidthread

        latencywrite = self.latencywrite

        latencyread = self.latencyread

        latencyreadcold = self.latencyreadcold

        colddata = self.colddata

        localzoneread = self.localzoneread

        failureperformance = self.failureperformance

        capacityreservation = self.capacityreservation

        resiliencymedia = self.resiliencymedia

        resiliencynode = self.resiliencynode

        resiliencyzone = self.resiliencyzone

        resiliencyregion = self.resiliencyregion

        replicationrpo = self.replicationrpo

        replicationbandwidth = self.replicationbandwidth

        encryption = self.encryption

        sed = self.sed

        integrity = self.integrity

        snapshotkeep = self.snapshotkeep

        snapshotfrequency = self.snapshotfrequency

        snapshotday = self.snapshotday

        snapshothour = self.snapshothour

        snapshotminute = self.snapshotminute

        createdbyuser_name = self.createdbyuser_name

        createdbyuseremail = self.createdbyuseremail

        createdtime = self.createdtime

        updatebyusername = self.updatebyusername

        updateby_useremail = self.updateby_useremail

        updatetime = self.updatetime

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "capacityoptimization": capacityoptimization,
            }
        )
        if iopswrite is not UNSET:
            field_dict["iopswrite"] = iopswrite
        if iopsread is not UNSET:
            field_dict["iopsread"] = iopsread
        if bandwidthwrite is not UNSET:
            field_dict["bandwidthwrite"] = bandwidthwrite
        if bandwidthread is not UNSET:
            field_dict["bandwidthread"] = bandwidthread
        if latencywrite is not UNSET:
            field_dict["latencywrite"] = latencywrite
        if latencyread is not UNSET:
            field_dict["latencyread"] = latencyread
        if latencyreadcold is not UNSET:
            field_dict["latencyreadcold"] = latencyreadcold
        if colddata is not UNSET:
            field_dict["colddata"] = colddata
        if localzoneread is not UNSET:
            field_dict["localzoneread"] = localzoneread
        if failureperformance is not UNSET:
            field_dict["failureperformance"] = failureperformance
        if capacityreservation is not UNSET:
            field_dict["capacityreservation"] = capacityreservation
        if resiliencymedia is not UNSET:
            field_dict["resiliencymedia"] = resiliencymedia
        if resiliencynode is not UNSET:
            field_dict["resiliencynode"] = resiliencynode
        if resiliencyzone is not UNSET:
            field_dict["resiliencyzone"] = resiliencyzone
        if resiliencyregion is not UNSET:
            field_dict["resiliencyregion"] = resiliencyregion
        if replicationrpo is not UNSET:
            field_dict["replicationrpo"] = replicationrpo
        if replicationbandwidth is not UNSET:
            field_dict["replicationbandwidth"] = replicationbandwidth
        if encryption is not UNSET:
            field_dict["encryption"] = encryption
        if sed is not UNSET:
            field_dict["sed"] = sed
        if integrity is not UNSET:
            field_dict["integrity"] = integrity
        if snapshotkeep is not UNSET:
            field_dict["snapshotkeep"] = snapshotkeep
        if snapshotfrequency is not UNSET:
            field_dict["snapshotfrequency"] = snapshotfrequency
        if snapshotday is not UNSET:
            field_dict["snapshotday"] = snapshotday
        if snapshothour is not UNSET:
            field_dict["snapshothour"] = snapshothour
        if snapshotminute is not UNSET:
            field_dict["snapshotminute"] = snapshotminute
        if createdbyuser_name is not UNSET:
            field_dict["createdbyuserName"] = createdbyuser_name
        if createdbyuseremail is not UNSET:
            field_dict["createdbyuseremail"] = createdbyuseremail
        if createdtime is not UNSET:
            field_dict["createdtime"] = createdtime
        if updatebyusername is not UNSET:
            field_dict["updatebyusername"] = updatebyusername
        if updateby_useremail is not UNSET:
            field_dict["updatebyUseremail"] = updateby_useremail
        if updatetime is not UNSET:
            field_dict["updatetime"] = updatetime

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        capacityoptimization = PolicyCapacityoptimization(d.pop("capacityoptimization"))

        iopswrite = d.pop("iopswrite", UNSET)

        iopsread = d.pop("iopsread", UNSET)

        bandwidthwrite = d.pop("bandwidthwrite", UNSET)

        bandwidthread = d.pop("bandwidthread", UNSET)

        latencywrite = d.pop("latencywrite", UNSET)

        latencyread = d.pop("latencyread", UNSET)

        latencyreadcold = d.pop("latencyreadcold", UNSET)

        colddata = d.pop("colddata", UNSET)

        localzoneread = d.pop("localzoneread", UNSET)

        failureperformance = d.pop("failureperformance", UNSET)

        capacityreservation = d.pop("capacityreservation", UNSET)

        resiliencymedia = d.pop("resiliencymedia", UNSET)

        resiliencynode = d.pop("resiliencynode", UNSET)

        resiliencyzone = d.pop("resiliencyzone", UNSET)

        resiliencyregion = d.pop("resiliencyregion", UNSET)

        replicationrpo = d.pop("replicationrpo", UNSET)

        replicationbandwidth = d.pop("replicationbandwidth", UNSET)

        encryption = d.pop("encryption", UNSET)

        sed = d.pop("sed", UNSET)

        integrity = d.pop("integrity", UNSET)

        snapshotkeep = d.pop("snapshotkeep", UNSET)

        snapshotfrequency = d.pop("snapshotfrequency", UNSET)

        snapshotday = d.pop("snapshotday", UNSET)

        snapshothour = d.pop("snapshothour", UNSET)

        snapshotminute = d.pop("snapshotminute", UNSET)

        createdbyuser_name = d.pop("createdbyuserName", UNSET)

        createdbyuseremail = d.pop("createdbyuseremail", UNSET)

        createdtime = d.pop("createdtime", UNSET)

        updatebyusername = d.pop("updatebyusername", UNSET)

        updateby_useremail = d.pop("updatebyUseremail", UNSET)

        updatetime = d.pop("updatetime", UNSET)

        policy = cls(
            name=name,
            capacityoptimization=capacityoptimization,
            iopswrite=iopswrite,
            iopsread=iopsread,
            bandwidthwrite=bandwidthwrite,
            bandwidthread=bandwidthread,
            latencywrite=latencywrite,
            latencyread=latencyread,
            latencyreadcold=latencyreadcold,
            colddata=colddata,
            localzoneread=localzoneread,
            failureperformance=failureperformance,
            capacityreservation=capacityreservation,
            resiliencymedia=resiliencymedia,
            resiliencynode=resiliencynode,
            resiliencyzone=resiliencyzone,
            resiliencyregion=resiliencyregion,
            replicationrpo=replicationrpo,
            replicationbandwidth=replicationbandwidth,
            encryption=encryption,
            sed=sed,
            integrity=integrity,
            snapshotkeep=snapshotkeep,
            snapshotfrequency=snapshotfrequency,
            snapshotday=snapshotday,
            snapshothour=snapshothour,
            snapshotminute=snapshotminute,
            createdbyuser_name=createdbyuser_name,
            createdbyuseremail=createdbyuseremail,
            createdtime=createdtime,
            updatebyusername=updatebyusername,
            updateby_useremail=updateby_useremail,
            updatetime=updatetime,
        )

        policy.additional_properties = d
        return policy

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
