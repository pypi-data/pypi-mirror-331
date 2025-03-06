from typing import Any, Dict, List, Type, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="RestartInstanceBody")


@_attrs_define
class RestartInstanceBody:
    """
    Attributes:
        instance_ids (List[str]): The unique identifiers (IDs) of the instances to restart
    """

    instance_ids: List[str]

    def to_dict(self) -> Dict[str, Any]:
        instance_ids = self.instance_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "instance_ids": instance_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        instance_ids = cast(List[str], d.pop("instance_ids"))

        restart_instance_body = cls(
            instance_ids=instance_ids,
        )

        return restart_instance_body
