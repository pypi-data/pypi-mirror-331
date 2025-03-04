from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RefreshTokenResponse")


@_attrs_define
class RefreshTokenResponse:
    """
    Attributes:
        access_token (Union[Unset, str]):
        id_token (Union[Unset, str]):
        access_token_expiration (Union[Unset, str]):
        id_token_expiration (Union[Unset, str]):
        token_type (Union[Unset, str]):
    """

    access_token: Union[Unset, str] = UNSET
    id_token: Union[Unset, str] = UNSET
    access_token_expiration: Union[Unset, str] = UNSET
    id_token_expiration: Union[Unset, str] = UNSET
    token_type: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        access_token = self.access_token

        id_token = self.id_token

        access_token_expiration = self.access_token_expiration

        id_token_expiration = self.id_token_expiration

        token_type = self.token_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if access_token is not UNSET:
            field_dict["AccessToken"] = access_token
        if id_token is not UNSET:
            field_dict["IdToken"] = id_token
        if access_token_expiration is not UNSET:
            field_dict["AccessTokenExpiration"] = access_token_expiration
        if id_token_expiration is not UNSET:
            field_dict["IdTokenExpiration"] = id_token_expiration
        if token_type is not UNSET:
            field_dict["TokenType"] = token_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        access_token = d.pop("AccessToken", UNSET)

        id_token = d.pop("IdToken", UNSET)

        access_token_expiration = d.pop("AccessTokenExpiration", UNSET)

        id_token_expiration = d.pop("IdTokenExpiration", UNSET)

        token_type = d.pop("TokenType", UNSET)

        refresh_token_response = cls(
            access_token=access_token,
            id_token=id_token,
            access_token_expiration=access_token_expiration,
            id_token_expiration=id_token_expiration,
            token_type=token_type,
        )

        refresh_token_response.additional_properties = d
        return refresh_token_response

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
