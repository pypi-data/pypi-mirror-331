from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="TenantCreateAdminUserRequest")


@_attrs_define
class TenantCreateAdminUserRequest:
    """
    Attributes:
        email (str):
        password (str):
        name (str):
        cloudprovider (Union[Unset, str]):
        markettoken (Union[Unset, str]):
    """

    email: str
    password: str
    name: str
    cloudprovider: Union[Unset, str] = UNSET
    markettoken: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        password = self.password

        name = self.name

        cloudprovider = self.cloudprovider

        markettoken = self.markettoken

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email": email,
                "password": password,
                "name": name,
            }
        )
        if cloudprovider is not UNSET:
            field_dict["cloudprovider"] = cloudprovider
        if markettoken is not UNSET:
            field_dict["markettoken"] = markettoken

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        email = d.pop("email")

        password = d.pop("password")

        name = d.pop("name")

        cloudprovider = d.pop("cloudprovider", UNSET)

        markettoken = d.pop("markettoken", UNSET)

        tenant_create_admin_user_request = cls(
            email=email,
            password=password,
            name=name,
            cloudprovider=cloudprovider,
            markettoken=markettoken,
        )

        tenant_create_admin_user_request.additional_properties = d
        return tenant_create_admin_user_request

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
