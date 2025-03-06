from typing import Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="AddSSHKeyBody")


@_attrs_define
class AddSSHKeyBody:
    """The name for the SSH key. Optionally, an existing public key can be supplied for the `public_key` property. If the
    `public_key` property is omitted, a new key pair is generated. The private key is returned in the response.

        Example:
            {'name': 'newly-generated-key'}

        Attributes:
            name (str): Name of the SSH key Example: macbook-pro.
            public_key (Union[Unset, str]): Public key for the SSH key Example: ssh-rsa
                AAAAB3NzaC1yc2EAAAADAQABAAABAQDfKpav4ILY54InZe27G user.
    """

    name: str
    public_key: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        public_key = self.public_key

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "name": name,
            }
        )
        if public_key is not UNSET:
            field_dict["public_key"] = public_key

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        public_key = d.pop("public_key", UNSET)

        add_ssh_key_body = cls(
            name=name,
            public_key=public_key,
        )

        return add_ssh_key_body
