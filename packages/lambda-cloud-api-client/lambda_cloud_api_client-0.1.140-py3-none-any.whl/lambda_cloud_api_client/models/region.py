from typing import Any, Dict, Type, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="Region")


@_attrs_define
class Region:
    """
    Attributes:
        name (str): Short name of a region Example: us-tx-1.
        description (str): Long name of a region Example: Austin, Texas.
    """

    name: str
    description: str

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        description = self.description

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "name": name,
                "description": description,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        description = d.pop("description")

        region = cls(
            name=name,
            description=description,
        )

        return region
