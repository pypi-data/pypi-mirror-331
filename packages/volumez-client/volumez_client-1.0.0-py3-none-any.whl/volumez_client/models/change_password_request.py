from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ChangePasswordRequest")


@_attrs_define
class ChangePasswordRequest:
    """
    Attributes:
        password (Union[Unset, str]):
        name (Union[Unset, str]):
        guid (Union[Unset, str]):
    """

    password: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    guid: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        password = self.password

        name = self.name

        guid = self.guid

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if password is not UNSET:
            field_dict["password"] = password
        if name is not UNSET:
            field_dict["name"] = name
        if guid is not UNSET:
            field_dict["guid"] = guid

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        password = d.pop("password", UNSET)

        name = d.pop("name", UNSET)

        guid = d.pop("guid", UNSET)

        change_password_request = cls(
            password=password,
            name=name,
            guid=guid,
        )

        change_password_request.additional_properties = d
        return change_password_request

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
