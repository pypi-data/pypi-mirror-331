from typing import Any, Dict, Type, TypeVar, Union, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="SshKey")


@_attrs_define
class SshKey:
    """Information about a stored SSH key, which can be used to access instances over SSH

    Attributes:
        id (str): Unique identifier (ID) of an SSH key Example: 0920582c7ff041399e34823a0be62548.
        name (str): Name of the SSH key Example: macbook-pro.
        public_key (str): Public key for the SSH key Example: ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDfKpav4ILY54InZe27G
            user.
        private_key (Union[None, Unset, str]): Private key for the SSH key. Only returned when generating a new key
            pair. Example: -----BEGIN RSA PRIVATE KEY-----
            MIIEpQIBAAKCAQEA5IGybv8/wdQM6Y4yYTGiEem4TscBZiAW+9xyW2pDt8S7VDtm
            ...
            eCW4938W9u8N3R/kpGwi1tZYiGMLBU4Ks0qKFi/VeEaE9OLeP5WQ8Pk=
            -----END RSA PRIVATE KEY-----
            .
    """

    id: str
    name: str
    public_key: str
    private_key: Union[None, Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        name = self.name

        public_key = self.public_key

        private_key: Union[None, Unset, str]
        if isinstance(self.private_key, Unset):
            private_key = UNSET
        else:
            private_key = self.private_key

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "name": name,
                "public_key": public_key,
            }
        )
        if private_key is not UNSET:
            field_dict["private_key"] = private_key

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        public_key = d.pop("public_key")

        def _parse_private_key(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        private_key = _parse_private_key(d.pop("private_key", UNSET))

        ssh_key = cls(
            id=id,
            name=name,
            public_key=public_key,
            private_key=private_key,
        )

        return ssh_key
