from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.auto_provision_volume_os_type import AutoProvisionVolumeOsType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.auto_provision_infra_plan import AutoProvisionInfraPlan
    from ..models.volume import Volume


T = TypeVar("T", bound="AutoProvisionVolume")


@_attrs_define
class AutoProvisionVolume:
    """
    Attributes:
        volume (Volume):
        cloud_provider (str):  Example: Aws.
        account_id (str):
        region (str):  Example: us-east-1.
        availability_zones (list[str]):
        subnets (list[str]):
        os_type (AutoProvisionVolumeOsType):
        infra_plan (Union[Unset, AutoProvisionInfraPlan]):
        ssh_key_name (Union[Unset, str]):
        image_id (Union[Unset, str]):
    """

    volume: "Volume"
    cloud_provider: str
    account_id: str
    region: str
    availability_zones: list[str]
    subnets: list[str]
    os_type: AutoProvisionVolumeOsType
    infra_plan: Union[Unset, "AutoProvisionInfraPlan"] = UNSET
    ssh_key_name: Union[Unset, str] = UNSET
    image_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        volume = self.volume.to_dict()

        cloud_provider = self.cloud_provider

        account_id = self.account_id

        region = self.region

        availability_zones = self.availability_zones

        subnets = self.subnets

        os_type = self.os_type.value

        infra_plan: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.infra_plan, Unset):
            infra_plan = self.infra_plan.to_dict()

        ssh_key_name = self.ssh_key_name

        image_id = self.image_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "volume": volume,
                "cloudProvider": cloud_provider,
                "accountId": account_id,
                "region": region,
                "availabilityZones": availability_zones,
                "subnets": subnets,
                "osType": os_type,
            }
        )
        if infra_plan is not UNSET:
            field_dict["infraPlan"] = infra_plan
        if ssh_key_name is not UNSET:
            field_dict["sshKeyName"] = ssh_key_name
        if image_id is not UNSET:
            field_dict["imageId"] = image_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.auto_provision_infra_plan import AutoProvisionInfraPlan
        from ..models.volume import Volume

        d = src_dict.copy()
        volume = Volume.from_dict(d.pop("volume"))

        cloud_provider = d.pop("cloudProvider")

        account_id = d.pop("accountId")

        region = d.pop("region")

        availability_zones = cast(list[str], d.pop("availabilityZones"))

        subnets = cast(list[str], d.pop("subnets"))

        os_type = AutoProvisionVolumeOsType(d.pop("osType"))

        _infra_plan = d.pop("infraPlan", UNSET)
        infra_plan: Union[Unset, AutoProvisionInfraPlan]
        if isinstance(_infra_plan, Unset):
            infra_plan = UNSET
        else:
            infra_plan = AutoProvisionInfraPlan.from_dict(_infra_plan)

        ssh_key_name = d.pop("sshKeyName", UNSET)

        image_id = d.pop("imageId", UNSET)

        auto_provision_volume = cls(
            volume=volume,
            cloud_provider=cloud_provider,
            account_id=account_id,
            region=region,
            availability_zones=availability_zones,
            subnets=subnets,
            os_type=os_type,
            infra_plan=infra_plan,
            ssh_key_name=ssh_key_name,
            image_id=image_id,
        )

        auto_provision_volume.additional_properties = d
        return auto_provision_volume

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
