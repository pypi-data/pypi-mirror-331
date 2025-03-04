from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="TenantTokenResponse")


@_attrs_define
class TenantTokenResponse:
    """
    Attributes:
        access_token (str):
        token_type (str):
        expires_in (int):
    """

    access_token: str
    token_type: str
    expires_in: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        access_token = self.access_token

        token_type = self.token_type

        expires_in = self.expires_in

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "AccessToken": access_token,
                "TokenType": token_type,
                "ExpiresIn": expires_in,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        access_token = d.pop("AccessToken")

        token_type = d.pop("TokenType")

        expires_in = d.pop("ExpiresIn")

        tenant_token_response = cls(
            access_token=access_token,
            token_type=token_type,
            expires_in=expires_in,
        )

        tenant_token_response.additional_properties = d
        return tenant_token_response

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
