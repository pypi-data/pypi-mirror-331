from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ChangePasswordRequestLoggedIn")


@_attrs_define
class ChangePasswordRequestLoggedIn:
    """
    Attributes:
        oldpassword (Union[Unset, str]):
        email (Union[Unset, str]):
        newpassword (Union[Unset, str]):
    """

    oldpassword: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    newpassword: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        oldpassword = self.oldpassword

        email = self.email

        newpassword = self.newpassword

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if oldpassword is not UNSET:
            field_dict["oldpassword"] = oldpassword
        if email is not UNSET:
            field_dict["email"] = email
        if newpassword is not UNSET:
            field_dict["newpassword"] = newpassword

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        oldpassword = d.pop("oldpassword", UNSET)

        email = d.pop("email", UNSET)

        newpassword = d.pop("newpassword", UNSET)

        change_password_request_logged_in = cls(
            oldpassword=oldpassword,
            email=email,
            newpassword=newpassword,
        )

        change_password_request_logged_in.additional_properties = d
        return change_password_request_logged_in

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
