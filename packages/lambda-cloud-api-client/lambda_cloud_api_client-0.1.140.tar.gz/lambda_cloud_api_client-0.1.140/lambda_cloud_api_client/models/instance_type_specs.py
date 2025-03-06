from typing import Any, Dict, Type, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="InstanceTypeSpecs")


@_attrs_define
class InstanceTypeSpecs:
    """
    Attributes:
        vcpus (int): Number of virtual CPUs Example: 24.
        memory_gib (int): Amount of RAM, in gibibytes (GiB) Example: 800.
        storage_gib (int): Amount of storage, in gibibytes (GiB). Example: 512.
        gpus (int): Number of GPUs Example: 4.
    """

    vcpus: int
    memory_gib: int
    storage_gib: int
    gpus: int

    def to_dict(self) -> Dict[str, Any]:
        vcpus = self.vcpus

        memory_gib = self.memory_gib

        storage_gib = self.storage_gib

        gpus = self.gpus

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "vcpus": vcpus,
                "memory_gib": memory_gib,
                "storage_gib": storage_gib,
                "gpus": gpus,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        vcpus = d.pop("vcpus")

        memory_gib = d.pop("memory_gib")

        storage_gib = d.pop("storage_gib")

        gpus = d.pop("gpus")

        instance_type_specs = cls(
            vcpus=vcpus,
            memory_gib=memory_gib,
            storage_gib=storage_gib,
            gpus=gpus,
        )

        return instance_type_specs
