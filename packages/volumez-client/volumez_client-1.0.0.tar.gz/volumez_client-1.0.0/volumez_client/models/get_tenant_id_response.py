from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetTenantIDResponse")


@_attrs_define
class GetTenantIDResponse:
    """
    Attributes:
        status_code (int):
        message (Union[Unset, str]):
        tenant_id (Union[Unset, str]):
    """

    status_code: int
    message: Union[Unset, str] = UNSET
    tenant_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status_code = self.status_code

        message = self.message

        tenant_id = self.tenant_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "StatusCode": status_code,
            }
        )
        if message is not UNSET:
            field_dict["Message"] = message
        if tenant_id is not UNSET:
            field_dict["TenantID"] = tenant_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        status_code = d.pop("StatusCode")

        message = d.pop("Message", UNSET)

        tenant_id = d.pop("TenantID", UNSET)

        get_tenant_id_response = cls(
            status_code=status_code,
            message=message,
            tenant_id=tenant_id,
        )

        get_tenant_id_response.additional_properties = d
        return get_tenant_id_response

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
