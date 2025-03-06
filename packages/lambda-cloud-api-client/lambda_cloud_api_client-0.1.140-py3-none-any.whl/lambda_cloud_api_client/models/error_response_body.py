from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.error import Error
    from ..models.error_response_body_field_errors import ErrorResponseBodyFieldErrors


T = TypeVar("T", bound="ErrorResponseBody")


@_attrs_define
class ErrorResponseBody:
    """
    Attributes:
        error (Error):
        field_errors (Union[Unset, ErrorResponseBodyFieldErrors]): Details about errors on a per-parameter basis
    """

    error: "Error"
    field_errors: Union[Unset, "ErrorResponseBodyFieldErrors"] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        error = self.error.to_dict()

        field_errors: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.field_errors, Unset):
            field_errors = self.field_errors.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "error": error,
            }
        )
        if field_errors is not UNSET:
            field_dict["field_errors"] = field_errors

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.error import Error
        from ..models.error_response_body_field_errors import ErrorResponseBodyFieldErrors

        d = src_dict.copy()
        error = Error.from_dict(d.pop("error"))

        _field_errors = d.pop("field_errors", UNSET)
        field_errors: Union[Unset, ErrorResponseBodyFieldErrors]
        if isinstance(_field_errors, Unset):
            field_errors = UNSET
        else:
            field_errors = ErrorResponseBodyFieldErrors.from_dict(_field_errors)

        error_response_body = cls(
            error=error,
            field_errors=field_errors,
        )

        return error_response_body
