from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.error import Error


T = TypeVar("T", bound="ErrorResponseBodyFieldErrors")


@_attrs_define
class ErrorResponseBodyFieldErrors:
    """Details about errors on a per-parameter basis"""

    additional_properties: Dict[str, "Error"] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.error import Error

        d = src_dict.copy()
        error_response_body_field_errors = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = Error.from_dict(prop_dict)

            additional_properties[prop_name] = additional_property

        error_response_body_field_errors.additional_properties = additional_properties
        return error_response_body_field_errors

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> "Error":
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: "Error") -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
