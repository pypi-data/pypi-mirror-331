from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.job_args import JobArgs


T = TypeVar("T", bound="Job")


@_attrs_define
class Job:
    """
    Attributes:
        id (Union[Unset, int]):
        type_ (Union[Unset, str]):
        object_ (Union[Unset, str]):
        args (Union[Unset, JobArgs]):
        state (Union[Unset, str]):
        status (Union[Unset, str]):
        progress (Union[Unset, int]):
        starttime (Union[Unset, str]):
        endtime (Union[Unset, str]):
        username (Union[Unset, str]):
        useremail (Union[Unset, str]):
    """

    id: Union[Unset, int] = UNSET
    type_: Union[Unset, str] = UNSET
    object_: Union[Unset, str] = UNSET
    args: Union[Unset, "JobArgs"] = UNSET
    state: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    progress: Union[Unset, int] = UNSET
    starttime: Union[Unset, str] = UNSET
    endtime: Union[Unset, str] = UNSET
    username: Union[Unset, str] = UNSET
    useremail: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        type_ = self.type_

        object_ = self.object_

        args: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.args, Unset):
            args = self.args.to_dict()

        state = self.state

        status = self.status

        progress = self.progress

        starttime = self.starttime

        endtime = self.endtime

        username = self.username

        useremail = self.useremail

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if type_ is not UNSET:
            field_dict["type"] = type_
        if object_ is not UNSET:
            field_dict["object"] = object_
        if args is not UNSET:
            field_dict["args"] = args
        if state is not UNSET:
            field_dict["state"] = state
        if status is not UNSET:
            field_dict["status"] = status
        if progress is not UNSET:
            field_dict["progress"] = progress
        if starttime is not UNSET:
            field_dict["starttime"] = starttime
        if endtime is not UNSET:
            field_dict["endtime"] = endtime
        if username is not UNSET:
            field_dict["username"] = username
        if useremail is not UNSET:
            field_dict["useremail"] = useremail

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.job_args import JobArgs

        d = src_dict.copy()
        id = d.pop("id", UNSET)

        type_ = d.pop("type", UNSET)

        object_ = d.pop("object", UNSET)

        _args = d.pop("args", UNSET)
        args: Union[Unset, JobArgs]
        if isinstance(_args, Unset):
            args = UNSET
        else:
            args = JobArgs.from_dict(_args)

        state = d.pop("state", UNSET)

        status = d.pop("status", UNSET)

        progress = d.pop("progress", UNSET)

        starttime = d.pop("starttime", UNSET)

        endtime = d.pop("endtime", UNSET)

        username = d.pop("username", UNSET)

        useremail = d.pop("useremail", UNSET)

        job = cls(
            id=id,
            type_=type_,
            object_=object_,
            args=args,
            state=state,
            status=status,
            progress=progress,
            starttime=starttime,
            endtime=endtime,
            username=username,
            useremail=useremail,
        )

        job.additional_properties = d
        return job

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
