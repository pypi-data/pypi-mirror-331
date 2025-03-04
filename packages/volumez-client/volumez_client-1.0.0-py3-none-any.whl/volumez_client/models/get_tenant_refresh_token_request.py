from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GetTenantRefreshTokenRequest")


@_attrs_define
class GetTenantRefreshTokenRequest:
    """
    Attributes:
        accesstoken (str):
        hostname (str):
    """

    accesstoken: str
    hostname: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        accesstoken = self.accesstoken

        hostname = self.hostname

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "accesstoken": accesstoken,
                "hostname": hostname,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        accesstoken = d.pop("accesstoken")

        hostname = d.pop("hostname")

        get_tenant_refresh_token_request = cls(
            accesstoken=accesstoken,
            hostname=hostname,
        )

        get_tenant_refresh_token_request.additional_properties = d
        return get_tenant_refresh_token_request

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
