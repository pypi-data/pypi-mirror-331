from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.alert_alert_severity import AlertAlertSeverity
from ..models.alert_alert_state import AlertAlertState
from ..models.alert_alert_type import AlertAlertType
from ..models.alert_alert_underlying_object_type import AlertAlertUnderlyingObjectType
from ..types import UNSET, Unset

T = TypeVar("T", bound="Alert")


@_attrs_define
class Alert:
    """
    Attributes:
        alertid (Union[Unset, str]):
        type_ (Union[Unset, AlertAlertType]):
        state (Union[Unset, AlertAlertState]):
        severity (Union[Unset, AlertAlertSeverity]):
        objecttype (Union[Unset, AlertAlertUnderlyingObjectType]):
        objectid (Union[Unset, str]):
        creationtime (Union[Unset, str]):
        lastsendtime (Union[Unset, str]):
        cleartime (Union[Unset, str]):
        details (Union[Unset, str]):
    """

    alertid: Union[Unset, str] = UNSET
    type_: Union[Unset, AlertAlertType] = UNSET
    state: Union[Unset, AlertAlertState] = UNSET
    severity: Union[Unset, AlertAlertSeverity] = UNSET
    objecttype: Union[Unset, AlertAlertUnderlyingObjectType] = UNSET
    objectid: Union[Unset, str] = UNSET
    creationtime: Union[Unset, str] = UNSET
    lastsendtime: Union[Unset, str] = UNSET
    cleartime: Union[Unset, str] = UNSET
    details: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        alertid = self.alertid

        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        state: Union[Unset, str] = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.value

        severity: Union[Unset, str] = UNSET
        if not isinstance(self.severity, Unset):
            severity = self.severity.value

        objecttype: Union[Unset, str] = UNSET
        if not isinstance(self.objecttype, Unset):
            objecttype = self.objecttype.value

        objectid = self.objectid

        creationtime = self.creationtime

        lastsendtime = self.lastsendtime

        cleartime = self.cleartime

        details = self.details

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if alertid is not UNSET:
            field_dict["alertid"] = alertid
        if type_ is not UNSET:
            field_dict["type"] = type_
        if state is not UNSET:
            field_dict["state"] = state
        if severity is not UNSET:
            field_dict["severity"] = severity
        if objecttype is not UNSET:
            field_dict["objecttype"] = objecttype
        if objectid is not UNSET:
            field_dict["objectid"] = objectid
        if creationtime is not UNSET:
            field_dict["creationtime"] = creationtime
        if lastsendtime is not UNSET:
            field_dict["lastsendtime"] = lastsendtime
        if cleartime is not UNSET:
            field_dict["cleartime"] = cleartime
        if details is not UNSET:
            field_dict["details"] = details

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        alertid = d.pop("alertid", UNSET)

        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, AlertAlertType]
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = AlertAlertType(_type_)

        _state = d.pop("state", UNSET)
        state: Union[Unset, AlertAlertState]
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = AlertAlertState(_state)

        _severity = d.pop("severity", UNSET)
        severity: Union[Unset, AlertAlertSeverity]
        if isinstance(_severity, Unset):
            severity = UNSET
        else:
            severity = AlertAlertSeverity(_severity)

        _objecttype = d.pop("objecttype", UNSET)
        objecttype: Union[Unset, AlertAlertUnderlyingObjectType]
        if isinstance(_objecttype, Unset):
            objecttype = UNSET
        else:
            objecttype = AlertAlertUnderlyingObjectType(_objecttype)

        objectid = d.pop("objectid", UNSET)

        creationtime = d.pop("creationtime", UNSET)

        lastsendtime = d.pop("lastsendtime", UNSET)

        cleartime = d.pop("cleartime", UNSET)

        details = d.pop("details", UNSET)

        alert = cls(
            alertid=alertid,
            type_=type_,
            state=state,
            severity=severity,
            objecttype=objecttype,
            objectid=objectid,
            creationtime=creationtime,
            lastsendtime=lastsendtime,
            cleartime=cleartime,
            details=details,
        )

        alert.additional_properties = d
        return alert

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
