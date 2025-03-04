from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.attachment import Attachment


T = TypeVar("T", bound="VolumeGroup")


@_attrs_define
class VolumeGroup:
    """
    Attributes:
        volumegroupname (Union[Unset, str]):
        encryption (Union[Unset, bool]):
        integrity (Union[Unset, bool]):
        allocation (Union[Unset, str]):
        compression (Union[Unset, bool]):
        deduplication (Union[Unset, bool]):
        writecache (Union[Unset, bool]):
        redundancy (Union[Unset, int]):
        size (Union[Unset, int]):
        targetsecret (Union[Unset, str]):
        allocatedsize (Union[Unset, int]):
        resiliency (Union[Unset, str]):
        raidcolumns (Union[Unset, int]):
        mediasize (Union[Unset, int]):
        mediabandwidthwrite (Union[Unset, int]):
        mediabandwidthread (Union[Unset, int]):
        mediaiopswrite (Union[Unset, int]):
        mediaiopsread (Union[Unset, int]):
        media (Union[Unset, list[str]]):
        cachesize (Union[Unset, int]):
        cacheresiliency (Union[Unset, str]):
        cacheredundancy (Union[Unset, int]):
        cacheraidcolumns (Union[Unset, int]):
        cachemediasize (Union[Unset, int]):
        cachemediabandwidthwrite (Union[Unset, int]):
        cachemediabandwidthread (Union[Unset, int]):
        cachemediaiopswrite (Union[Unset, int]):
        cachemediaiopsread (Union[Unset, int]):
        cachemedia (Union[Unset, list[str]]):
        attachments (Union[Unset, list['Attachment']]):
    """

    volumegroupname: Union[Unset, str] = UNSET
    encryption: Union[Unset, bool] = UNSET
    integrity: Union[Unset, bool] = UNSET
    allocation: Union[Unset, str] = UNSET
    compression: Union[Unset, bool] = UNSET
    deduplication: Union[Unset, bool] = UNSET
    writecache: Union[Unset, bool] = UNSET
    redundancy: Union[Unset, int] = UNSET
    size: Union[Unset, int] = UNSET
    targetsecret: Union[Unset, str] = UNSET
    allocatedsize: Union[Unset, int] = UNSET
    resiliency: Union[Unset, str] = UNSET
    raidcolumns: Union[Unset, int] = UNSET
    mediasize: Union[Unset, int] = UNSET
    mediabandwidthwrite: Union[Unset, int] = UNSET
    mediabandwidthread: Union[Unset, int] = UNSET
    mediaiopswrite: Union[Unset, int] = UNSET
    mediaiopsread: Union[Unset, int] = UNSET
    media: Union[Unset, list[str]] = UNSET
    cachesize: Union[Unset, int] = UNSET
    cacheresiliency: Union[Unset, str] = UNSET
    cacheredundancy: Union[Unset, int] = UNSET
    cacheraidcolumns: Union[Unset, int] = UNSET
    cachemediasize: Union[Unset, int] = UNSET
    cachemediabandwidthwrite: Union[Unset, int] = UNSET
    cachemediabandwidthread: Union[Unset, int] = UNSET
    cachemediaiopswrite: Union[Unset, int] = UNSET
    cachemediaiopsread: Union[Unset, int] = UNSET
    cachemedia: Union[Unset, list[str]] = UNSET
    attachments: Union[Unset, list["Attachment"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        volumegroupname = self.volumegroupname

        encryption = self.encryption

        integrity = self.integrity

        allocation = self.allocation

        compression = self.compression

        deduplication = self.deduplication

        writecache = self.writecache

        redundancy = self.redundancy

        size = self.size

        targetsecret = self.targetsecret

        allocatedsize = self.allocatedsize

        resiliency = self.resiliency

        raidcolumns = self.raidcolumns

        mediasize = self.mediasize

        mediabandwidthwrite = self.mediabandwidthwrite

        mediabandwidthread = self.mediabandwidthread

        mediaiopswrite = self.mediaiopswrite

        mediaiopsread = self.mediaiopsread

        media: Union[Unset, list[str]] = UNSET
        if not isinstance(self.media, Unset):
            media = self.media

        cachesize = self.cachesize

        cacheresiliency = self.cacheresiliency

        cacheredundancy = self.cacheredundancy

        cacheraidcolumns = self.cacheraidcolumns

        cachemediasize = self.cachemediasize

        cachemediabandwidthwrite = self.cachemediabandwidthwrite

        cachemediabandwidthread = self.cachemediabandwidthread

        cachemediaiopswrite = self.cachemediaiopswrite

        cachemediaiopsread = self.cachemediaiopsread

        cachemedia: Union[Unset, list[str]] = UNSET
        if not isinstance(self.cachemedia, Unset):
            cachemedia = self.cachemedia

        attachments: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.attachments, Unset):
            attachments = []
            for attachments_item_data in self.attachments:
                attachments_item = attachments_item_data.to_dict()
                attachments.append(attachments_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if volumegroupname is not UNSET:
            field_dict["Volumegroupname"] = volumegroupname
        if encryption is not UNSET:
            field_dict["encryption"] = encryption
        if integrity is not UNSET:
            field_dict["Integrity"] = integrity
        if allocation is not UNSET:
            field_dict["allocation"] = allocation
        if compression is not UNSET:
            field_dict["compression"] = compression
        if deduplication is not UNSET:
            field_dict["deduplication"] = deduplication
        if writecache is not UNSET:
            field_dict["writecache"] = writecache
        if redundancy is not UNSET:
            field_dict["redundancy"] = redundancy
        if size is not UNSET:
            field_dict["size"] = size
        if targetsecret is not UNSET:
            field_dict["targetsecret"] = targetsecret
        if allocatedsize is not UNSET:
            field_dict["allocatedsize"] = allocatedsize
        if resiliency is not UNSET:
            field_dict["resiliency"] = resiliency
        if raidcolumns is not UNSET:
            field_dict["raidcolumns"] = raidcolumns
        if mediasize is not UNSET:
            field_dict["mediasize"] = mediasize
        if mediabandwidthwrite is not UNSET:
            field_dict["mediabandwidthwrite"] = mediabandwidthwrite
        if mediabandwidthread is not UNSET:
            field_dict["mediabandwidthread"] = mediabandwidthread
        if mediaiopswrite is not UNSET:
            field_dict["mediaiopswrite"] = mediaiopswrite
        if mediaiopsread is not UNSET:
            field_dict["mediaiopsread"] = mediaiopsread
        if media is not UNSET:
            field_dict["media"] = media
        if cachesize is not UNSET:
            field_dict["cachesize"] = cachesize
        if cacheresiliency is not UNSET:
            field_dict["cacheresiliency"] = cacheresiliency
        if cacheredundancy is not UNSET:
            field_dict["cacheredundancy"] = cacheredundancy
        if cacheraidcolumns is not UNSET:
            field_dict["cacheraidcolumns"] = cacheraidcolumns
        if cachemediasize is not UNSET:
            field_dict["cachemediasize"] = cachemediasize
        if cachemediabandwidthwrite is not UNSET:
            field_dict["cachemediabandwidthwrite"] = cachemediabandwidthwrite
        if cachemediabandwidthread is not UNSET:
            field_dict["cachemediabandwidthread"] = cachemediabandwidthread
        if cachemediaiopswrite is not UNSET:
            field_dict["cachemediaiopswrite"] = cachemediaiopswrite
        if cachemediaiopsread is not UNSET:
            field_dict["cachemediaiopsread"] = cachemediaiopsread
        if cachemedia is not UNSET:
            field_dict["cachemedia"] = cachemedia
        if attachments is not UNSET:
            field_dict["attachments"] = attachments

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.attachment import Attachment

        d = src_dict.copy()
        volumegroupname = d.pop("Volumegroupname", UNSET)

        encryption = d.pop("encryption", UNSET)

        integrity = d.pop("Integrity", UNSET)

        allocation = d.pop("allocation", UNSET)

        compression = d.pop("compression", UNSET)

        deduplication = d.pop("deduplication", UNSET)

        writecache = d.pop("writecache", UNSET)

        redundancy = d.pop("redundancy", UNSET)

        size = d.pop("size", UNSET)

        targetsecret = d.pop("targetsecret", UNSET)

        allocatedsize = d.pop("allocatedsize", UNSET)

        resiliency = d.pop("resiliency", UNSET)

        raidcolumns = d.pop("raidcolumns", UNSET)

        mediasize = d.pop("mediasize", UNSET)

        mediabandwidthwrite = d.pop("mediabandwidthwrite", UNSET)

        mediabandwidthread = d.pop("mediabandwidthread", UNSET)

        mediaiopswrite = d.pop("mediaiopswrite", UNSET)

        mediaiopsread = d.pop("mediaiopsread", UNSET)

        media = cast(list[str], d.pop("media", UNSET))

        cachesize = d.pop("cachesize", UNSET)

        cacheresiliency = d.pop("cacheresiliency", UNSET)

        cacheredundancy = d.pop("cacheredundancy", UNSET)

        cacheraidcolumns = d.pop("cacheraidcolumns", UNSET)

        cachemediasize = d.pop("cachemediasize", UNSET)

        cachemediabandwidthwrite = d.pop("cachemediabandwidthwrite", UNSET)

        cachemediabandwidthread = d.pop("cachemediabandwidthread", UNSET)

        cachemediaiopswrite = d.pop("cachemediaiopswrite", UNSET)

        cachemediaiopsread = d.pop("cachemediaiopsread", UNSET)

        cachemedia = cast(list[str], d.pop("cachemedia", UNSET))

        attachments = []
        _attachments = d.pop("attachments", UNSET)
        for attachments_item_data in _attachments or []:
            attachments_item = Attachment.from_dict(attachments_item_data)

            attachments.append(attachments_item)

        volume_group = cls(
            volumegroupname=volumegroupname,
            encryption=encryption,
            integrity=integrity,
            allocation=allocation,
            compression=compression,
            deduplication=deduplication,
            writecache=writecache,
            redundancy=redundancy,
            size=size,
            targetsecret=targetsecret,
            allocatedsize=allocatedsize,
            resiliency=resiliency,
            raidcolumns=raidcolumns,
            mediasize=mediasize,
            mediabandwidthwrite=mediabandwidthwrite,
            mediabandwidthread=mediabandwidthread,
            mediaiopswrite=mediaiopswrite,
            mediaiopsread=mediaiopsread,
            media=media,
            cachesize=cachesize,
            cacheresiliency=cacheresiliency,
            cacheredundancy=cacheredundancy,
            cacheraidcolumns=cacheraidcolumns,
            cachemediasize=cachemediasize,
            cachemediabandwidthwrite=cachemediabandwidthwrite,
            cachemediabandwidthread=cachemediabandwidthread,
            cachemediaiopswrite=cachemediaiopswrite,
            cachemediaiopsread=cachemediaiopsread,
            cachemedia=cachemedia,
            attachments=attachments,
        )

        volume_group.additional_properties = d
        return volume_group

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
