from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.add_ssh_key_body import AddSSHKeyBody
from ...types import Response


def _get_kwargs(
    *,
    body: AddSSHKeyBody,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/ssh-keys",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Any]:
    if response.status_code == 200:
        return None
    if response.status_code == 401:
        return None
    if response.status_code == 403:
        return None
    if response.status_code == 400:
        return None
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: AddSSHKeyBody,
) -> Response[Any]:
    r""" Add SSH key

     Add an SSH key

    To use an existing key pair, enter the public key for the `public_key` property of the request body.

    To generate a new key pair, omit the `public_key` property from the request body. Save the
    `private_key` from the response somewhere secure. For example, with curl:

    ```
    curl https://cloud.lambdalabs.com/api/v1/ssh-keys \
      --fail \
      -u ${LAMBDA_API_KEY}: \
      -X POST \
      -d '{\"name\": \"new key\"}' \
      | jq -r '.data.private_key' > key.pem

    chmod 400 key.pem
    ```

    Then, after you launch an instance with `new key` attached to it:
    ```
    ssh -i key.pem <instance IP>
    ```

    Args:
        body (AddSSHKeyBody): The name for the SSH key. Optionally, an existing public key can be
            supplied for the `public_key` property. If the `public_key` property is omitted, a new key
            pair is generated. The private key is returned in the response. Example: {'name': 'newly-
            generated-key'}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: AddSSHKeyBody,
) -> Response[Any]:
    r""" Add SSH key

     Add an SSH key

    To use an existing key pair, enter the public key for the `public_key` property of the request body.

    To generate a new key pair, omit the `public_key` property from the request body. Save the
    `private_key` from the response somewhere secure. For example, with curl:

    ```
    curl https://cloud.lambdalabs.com/api/v1/ssh-keys \
      --fail \
      -u ${LAMBDA_API_KEY}: \
      -X POST \
      -d '{\"name\": \"new key\"}' \
      | jq -r '.data.private_key' > key.pem

    chmod 400 key.pem
    ```

    Then, after you launch an instance with `new key` attached to it:
    ```
    ssh -i key.pem <instance IP>
    ```

    Args:
        body (AddSSHKeyBody): The name for the SSH key. Optionally, an existing public key can be
            supplied for the `public_key` property. If the `public_key` property is omitted, a new key
            pair is generated. The private key is returned in the response. Example: {'name': 'newly-
            generated-key'}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
