from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetTenanUserResponse")


@_attrs_define
class GetTenanUserResponse:
    """
    Attributes:
        status_code (Union[Unset, int]):
        message (Union[Unset, str]):
        email (Union[Unset, str]):
        name (Union[Unset, str]):
        tenant_id (Union[Unset, str]):
    """

    status_code: Union[Unset, int] = UNSET
    message: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    tenant_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status_code = self.status_code

        message = self.message

        email = self.email

        name = self.name

        tenant_id = self.tenant_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if status_code is not UNSET:
            field_dict["StatusCode"] = status_code
        if message is not UNSET:
            field_dict["Message"] = message
        if email is not UNSET:
            field_dict["Email"] = email
        if name is not UNSET:
            field_dict["Name"] = name
        if tenant_id is not UNSET:
            field_dict["TenantID"] = tenant_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        status_code = d.pop("StatusCode", UNSET)

        message = d.pop("Message", UNSET)

        email = d.pop("Email", UNSET)

        name = d.pop("Name", UNSET)

        tenant_id = d.pop("TenantID", UNSET)

        get_tenan_user_response = cls(
            status_code=status_code,
            message=message,
            email=email,
            name=name,
            tenant_id=tenant_id,
        )

        get_tenan_user_response.additional_properties = d
        return get_tenan_user_response

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
