from typing import Any, Dict, Type, TypeVar

from attrs import define as _attrs_define

from ..models.user_status import UserStatus

T = TypeVar("T", bound="User")


@_attrs_define
class User:
    """Information about a user in your team

    Attributes:
        id (str): Unique identifier for the user Example: 0920582c7ff041399e34823a0be62549.
        email (str): Email address of the user Example: teammate@example.com.
        status (UserStatus): Status of the user's account
    """

    id: str
    email: str
    status: UserStatus

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        email = self.email

        status = self.status.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "email": email,
                "status": status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        email = d.pop("email")

        status = UserStatus(d.pop("status"))

        user = cls(
            id=id,
            email=email,
            status=status,
        )

        return user
