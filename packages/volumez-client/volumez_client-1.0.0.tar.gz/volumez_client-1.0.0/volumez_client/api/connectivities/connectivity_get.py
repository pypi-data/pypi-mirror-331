from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.connectivity import Connectivity
from ...types import UNSET, Response, Unset


def _get_kwargs(
    connectivity: str,
    *,
    authorization: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/connectivities/{connectivity}",
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Connectivity]:
    if response.status_code == 200:
        response_200 = Connectivity.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Connectivity]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    connectivity: str,
    *,
    client: Union[AuthenticatedClient, Client],
    authorization: Union[Unset, str] = UNSET,
) -> Response[Connectivity]:
    """Get the properties of a connectivity

    Args:
        connectivity (str):
        authorization (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Connectivity]
    """

    kwargs = _get_kwargs(
        connectivity=connectivity,
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    connectivity: str,
    *,
    client: Union[AuthenticatedClient, Client],
    authorization: Union[Unset, str] = UNSET,
) -> Optional[Connectivity]:
    """Get the properties of a connectivity

    Args:
        connectivity (str):
        authorization (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Connectivity
    """

    return sync_detailed(
        connectivity=connectivity,
        client=client,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    connectivity: str,
    *,
    client: Union[AuthenticatedClient, Client],
    authorization: Union[Unset, str] = UNSET,
) -> Response[Connectivity]:
    """Get the properties of a connectivity

    Args:
        connectivity (str):
        authorization (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Connectivity]
    """

    kwargs = _get_kwargs(
        connectivity=connectivity,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    connectivity: str,
    *,
    client: Union[AuthenticatedClient, Client],
    authorization: Union[Unset, str] = UNSET,
) -> Optional[Connectivity]:
    """Get the properties of a connectivity

    Args:
        connectivity (str):
        authorization (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Connectivity
    """

    return (
        await asyncio_detailed(
            connectivity=connectivity,
            client=client,
            authorization=authorization,
        )
    ).parsed
