from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.authentication_chap import AuthenticationChap


T = TypeVar("T", bound="Authentication")


@_attrs_define
class Authentication:
    """
    Attributes:
        method (Union[Unset, str]):
        chap (Union[Unset, AuthenticationChap]):
    """

    method: Union[Unset, str] = UNSET
    chap: Union[Unset, "AuthenticationChap"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        method = self.method

        chap: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.chap, Unset):
            chap = self.chap.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if method is not UNSET:
            field_dict["method"] = method
        if chap is not UNSET:
            field_dict["chap"] = chap

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.authentication_chap import AuthenticationChap

        d = src_dict.copy()
        method = d.pop("method", UNSET)

        _chap = d.pop("chap", UNSET)
        chap: Union[Unset, AuthenticationChap]
        if isinstance(_chap, Unset):
            chap = UNSET
        else:
            chap = AuthenticationChap.from_dict(_chap)

        authentication = cls(
            method=method,
            chap=chap,
        )

        authentication.additional_properties = d
        return authentication

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
