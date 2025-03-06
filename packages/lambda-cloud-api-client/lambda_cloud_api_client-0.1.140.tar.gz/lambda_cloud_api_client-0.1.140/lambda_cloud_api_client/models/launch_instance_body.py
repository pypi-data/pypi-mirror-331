from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="LaunchInstanceBody")


@_attrs_define
class LaunchInstanceBody:
    """
    Attributes:
        region_name (str): Short name of a region Example: us-tx-1.
        instance_type_name (str): Name of an instance type Example: gpu_1x_a100.
        ssh_key_names (List[str]): Names of the SSH keys to allow access to the instances. Currently, exactly one SSH
            key must be specified.
        file_system_names (Union[Unset, List[str]]): Names of the file systems to attach to the instances. Currently,
            only one (if any) file system may be specified.
        quantity (Union[Unset, int]): Number of instances to launch Default: 1.
        name (Union[None, Unset, str]): User-provided name for the instance Example: training-node-1.
    """

    region_name: str
    instance_type_name: str
    ssh_key_names: List[str]
    file_system_names: Union[Unset, List[str]] = UNSET
    quantity: Union[Unset, int] = 1
    name: Union[None, Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        region_name = self.region_name

        instance_type_name = self.instance_type_name

        ssh_key_names = self.ssh_key_names

        file_system_names: Union[Unset, List[str]] = UNSET
        if not isinstance(self.file_system_names, Unset):
            file_system_names = self.file_system_names

        quantity = self.quantity

        name: Union[None, Unset, str]
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "region_name": region_name,
                "instance_type_name": instance_type_name,
                "ssh_key_names": ssh_key_names,
            }
        )
        if file_system_names is not UNSET:
            field_dict["file_system_names"] = file_system_names
        if quantity is not UNSET:
            field_dict["quantity"] = quantity
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        region_name = d.pop("region_name")

        instance_type_name = d.pop("instance_type_name")

        ssh_key_names = cast(List[str], d.pop("ssh_key_names"))

        file_system_names = cast(List[str], d.pop("file_system_names", UNSET))

        quantity = d.pop("quantity", UNSET)

        def _parse_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        name = _parse_name(d.pop("name", UNSET))

        launch_instance_body = cls(
            region_name=region_name,
            instance_type_name=instance_type_name,
            ssh_key_names=ssh_key_names,
            file_system_names=file_system_names,
            quantity=quantity,
            name=name,
        )

        return launch_instance_body
