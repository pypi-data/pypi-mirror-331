from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.region import Region
    from ..models.user import User


T = TypeVar("T", bound="FileSystem")


@_attrs_define
class FileSystem:
    """Information about a shared file system

    Attributes:
        id (str): Unique identifier (ID) of a file system Example: 0920582c7ff041399e34823a0be62547.
        name (str): Name of a file system Example: shared-fs.
        created (str): A date and time, formatted as an ISO 8601 time stamp Example: 2023-02-24T20:48:56+00:00.
        created_by (User): Information about a user in your team
        mount_point (str): Absolute path indicating where on instances the file system will be mounted Example:
            /home/ubuntu/shared-fs.
        region (Region):
        is_in_use (bool): Whether the file system is currently in use by an instance. File systems that are in use
            cannot be deleted.
        bytes_used (Union[Unset, int]): Approximate amount of storage used by the file system, in bytes. This value is
            an estimate that is updated every several hours. Example: 2147483648.
    """

    id: str
    name: str
    created: str
    created_by: "User"
    mount_point: str
    region: "Region"
    is_in_use: bool
    bytes_used: Union[Unset, int] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        name = self.name

        created = self.created

        created_by = self.created_by.to_dict()

        mount_point = self.mount_point

        region = self.region.to_dict()

        is_in_use = self.is_in_use

        bytes_used = self.bytes_used

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "name": name,
                "created": created,
                "created_by": created_by,
                "mount_point": mount_point,
                "region": region,
                "is_in_use": is_in_use,
            }
        )
        if bytes_used is not UNSET:
            field_dict["bytes_used"] = bytes_used

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.region import Region
        from ..models.user import User

        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        created = d.pop("created")

        created_by = User.from_dict(d.pop("created_by"))

        mount_point = d.pop("mount_point")

        region = Region.from_dict(d.pop("region"))

        is_in_use = d.pop("is_in_use")

        bytes_used = d.pop("bytes_used", UNSET)

        file_system = cls(
            id=id,
            name=name,
            created=created,
            created_by=created_by,
            mount_point=mount_point,
            region=region,
            is_in_use=is_in_use,
            bytes_used=bytes_used,
        )

        return file_system
