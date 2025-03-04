from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="SignInResponse")


@_attrs_define
class SignInResponse:
    """
    Attributes:
        access_token (str):
        id_token (str):
        refresh_token (str):
        expires_in (int):
        token_type (str):
    """

    access_token: str
    id_token: str
    refresh_token: str
    expires_in: int
    token_type: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        access_token = self.access_token

        id_token = self.id_token

        refresh_token = self.refresh_token

        expires_in = self.expires_in

        token_type = self.token_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "AccessToken": access_token,
                "IdToken": id_token,
                "RefreshToken": refresh_token,
                "ExpiresIn": expires_in,
                "TokenType": token_type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        access_token = d.pop("AccessToken")

        id_token = d.pop("IdToken")

        refresh_token = d.pop("RefreshToken")

        expires_in = d.pop("ExpiresIn")

        token_type = d.pop("TokenType")

        sign_in_response = cls(
            access_token=access_token,
            id_token=id_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
            token_type=token_type,
        )

        sign_in_response.additional_properties = d
        return sign_in_response

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
