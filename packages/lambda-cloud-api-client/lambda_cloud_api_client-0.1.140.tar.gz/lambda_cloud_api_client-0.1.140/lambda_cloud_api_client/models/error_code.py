from enum import Enum


class ErrorCode(str, Enum):
    GLOBALACCOUNT_INACTIVE = "global/account-inactive"
    GLOBALINVALID_ADDRESS = "global/invalid-address"
    GLOBALINVALID_API_KEY = "global/invalid-api-key"
    GLOBALINVALID_PARAMETERS = "global/invalid-parameters"
    GLOBALOBJECT_DOES_NOT_EXIST = "global/object-does-not-exist"
    GLOBALQUOTA_EXCEEDED = "global/quota-exceeded"
    GLOBALUNKNOWN = "global/unknown"
    INSTANCE_OPERATIONSLAUNCHFILE_SYSTEM_IN_WRONG_REGION = "instance-operations/launch/file-system-in-wrong-region"
    INSTANCE_OPERATIONSLAUNCHINSUFFICIENT_CAPACITY = "instance-operations/launch/insufficient-capacity"
    SSH_KEYSKEY_IN_USE = "ssh-keys/key-in-use"

    def __str__(self) -> str:
        return str(self.value)
