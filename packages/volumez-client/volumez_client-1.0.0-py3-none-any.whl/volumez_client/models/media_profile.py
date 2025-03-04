from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MediaProfile")


@_attrs_define
class MediaProfile:
    """
    Attributes:
        iopsread (Union[Unset, int]):
        iopswrite (Union[Unset, int]):
        bandwidthread (Union[Unset, int]):
        bandwidthwrite (Union[Unset, int]):
        latencyread (Union[Unset, int]):
        latencywrite (Union[Unset, int]):
        freeiopsread (Union[Unset, int]):
        freeiopswrite (Union[Unset, int]):
        freebandwidthread (Union[Unset, int]):
        freebandwidthwrite (Union[Unset, int]):
    """

    iopsread: Union[Unset, int] = UNSET
    iopswrite: Union[Unset, int] = UNSET
    bandwidthread: Union[Unset, int] = UNSET
    bandwidthwrite: Union[Unset, int] = UNSET
    latencyread: Union[Unset, int] = UNSET
    latencywrite: Union[Unset, int] = UNSET
    freeiopsread: Union[Unset, int] = UNSET
    freeiopswrite: Union[Unset, int] = UNSET
    freebandwidthread: Union[Unset, int] = UNSET
    freebandwidthwrite: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        iopsread = self.iopsread

        iopswrite = self.iopswrite

        bandwidthread = self.bandwidthread

        bandwidthwrite = self.bandwidthwrite

        latencyread = self.latencyread

        latencywrite = self.latencywrite

        freeiopsread = self.freeiopsread

        freeiopswrite = self.freeiopswrite

        freebandwidthread = self.freebandwidthread

        freebandwidthwrite = self.freebandwidthwrite

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if iopsread is not UNSET:
            field_dict["iopsread"] = iopsread
        if iopswrite is not UNSET:
            field_dict["iopswrite"] = iopswrite
        if bandwidthread is not UNSET:
            field_dict["bandwidthread"] = bandwidthread
        if bandwidthwrite is not UNSET:
            field_dict["bandwidthwrite"] = bandwidthwrite
        if latencyread is not UNSET:
            field_dict["latencyread"] = latencyread
        if latencywrite is not UNSET:
            field_dict["latencywrite"] = latencywrite
        if freeiopsread is not UNSET:
            field_dict["freeiopsread"] = freeiopsread
        if freeiopswrite is not UNSET:
            field_dict["freeiopswrite"] = freeiopswrite
        if freebandwidthread is not UNSET:
            field_dict["freebandwidthread"] = freebandwidthread
        if freebandwidthwrite is not UNSET:
            field_dict["freebandwidthwrite"] = freebandwidthwrite

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        iopsread = d.pop("iopsread", UNSET)

        iopswrite = d.pop("iopswrite", UNSET)

        bandwidthread = d.pop("bandwidthread", UNSET)

        bandwidthwrite = d.pop("bandwidthwrite", UNSET)

        latencyread = d.pop("latencyread", UNSET)

        latencywrite = d.pop("latencywrite", UNSET)

        freeiopsread = d.pop("freeiopsread", UNSET)

        freeiopswrite = d.pop("freeiopswrite", UNSET)

        freebandwidthread = d.pop("freebandwidthread", UNSET)

        freebandwidthwrite = d.pop("freebandwidthwrite", UNSET)

        media_profile = cls(
            iopsread=iopsread,
            iopswrite=iopswrite,
            bandwidthread=bandwidthread,
            bandwidthwrite=bandwidthwrite,
            latencyread=latencyread,
            latencywrite=latencywrite,
            freeiopsread=freeiopsread,
            freeiopswrite=freeiopswrite,
            freebandwidthread=freebandwidthread,
            freebandwidthwrite=freebandwidthwrite,
        )

        media_profile.additional_properties = d
        return media_profile

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
