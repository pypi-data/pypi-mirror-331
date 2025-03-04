from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SuccessJobResponse")


@_attrs_define
class SuccessJobResponse:
    """
    Attributes:
        message (Union[Unset, str]):
        job_id (Union[Unset, str]):
        object_id (Union[Unset, str]):
    """

    message: Union[Unset, str] = UNSET
    job_id: Union[Unset, str] = UNSET
    object_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        message = self.message

        job_id = self.job_id

        object_id = self.object_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if message is not UNSET:
            field_dict["Message"] = message
        if job_id is not UNSET:
            field_dict["JobID"] = job_id
        if object_id is not UNSET:
            field_dict["ObjectID"] = object_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        message = d.pop("Message", UNSET)

        job_id = d.pop("JobID", UNSET)

        object_id = d.pop("ObjectID", UNSET)

        success_job_response = cls(
            message=message,
            job_id=job_id,
            object_id=object_id,
        )

        success_job_response.additional_properties = d
        return success_job_response

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
