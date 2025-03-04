from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.virtual_media_flavor import VirtualMediaFlavor
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.media import Media


T = TypeVar("T", bound="VirtualMedia")


@_attrs_define
class VirtualMedia:
    """
    Attributes:
        media (Union[Unset, Media]):
        flavor (Union[Unset, VirtualMediaFlavor]):
        members (Union[Unset, list[str]]):
    """

    media: Union[Unset, "Media"] = UNSET
    flavor: Union[Unset, VirtualMediaFlavor] = UNSET
    members: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        media: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.media, Unset):
            media = self.media.to_dict()

        flavor: Union[Unset, str] = UNSET
        if not isinstance(self.flavor, Unset):
            flavor = self.flavor.value

        members: Union[Unset, list[str]] = UNSET
        if not isinstance(self.members, Unset):
            members = self.members

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if media is not UNSET:
            field_dict["media"] = media
        if flavor is not UNSET:
            field_dict["flavor"] = flavor
        if members is not UNSET:
            field_dict["members"] = members

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.media import Media

        d = src_dict.copy()
        _media = d.pop("media", UNSET)
        media: Union[Unset, Media]
        if isinstance(_media, Unset):
            media = UNSET
        else:
            media = Media.from_dict(_media)

        _flavor = d.pop("flavor", UNSET)
        flavor: Union[Unset, VirtualMediaFlavor]
        if isinstance(_flavor, Unset):
            flavor = UNSET
        else:
            flavor = VirtualMediaFlavor(_flavor)

        members = cast(list[str], d.pop("members", UNSET))

        virtual_media = cls(
            media=media,
            flavor=flavor,
            members=members,
        )

        virtual_media.additional_properties = d
        return virtual_media

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
