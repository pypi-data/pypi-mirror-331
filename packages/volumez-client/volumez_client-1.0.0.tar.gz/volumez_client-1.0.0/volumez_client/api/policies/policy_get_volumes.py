from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.volume import Volume
from ...types import Response


def _get_kwargs(
    policy: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/policies/{policy}/volumes",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[list["Volume"]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Volume.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["Volume"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    policy: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[list["Volume"]]:
    """Get the properties of a policy

    Args:
        policy (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['Volume']]
    """

    kwargs = _get_kwargs(
        policy=policy,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    policy: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[list["Volume"]]:
    """Get the properties of a policy

    Args:
        policy (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['Volume']
    """

    return sync_detailed(
        policy=policy,
        client=client,
    ).parsed


async def asyncio_detailed(
    policy: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[list["Volume"]]:
    """Get the properties of a policy

    Args:
        policy (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['Volume']]
    """

    kwargs = _get_kwargs(
        policy=policy,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    policy: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[list["Volume"]]:
    """Get the properties of a policy

    Args:
        policy (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['Volume']
    """

    return (
        await asyncio_detailed(
            policy=policy,
            client=client,
        )
    ).parsed
