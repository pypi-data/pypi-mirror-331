from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.virtual_media import VirtualMedia
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    startfrom: Union[Unset, str] = UNSET,
    count: Union[Unset, int] = UNSET,
    authorization: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    params: dict[str, Any] = {}

    params["startfrom"] = startfrom

    params["count"] = count

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/virtualmedia",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[list["VirtualMedia"]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = VirtualMedia.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[list["VirtualMedia"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    startfrom: Union[Unset, str] = UNSET,
    count: Union[Unset, int] = UNSET,
    authorization: Union[Unset, str] = UNSET,
) -> Response[list["VirtualMedia"]]:
    """Get a list of virtual media

    Args:
        startfrom (Union[Unset, str]):
        count (Union[Unset, int]):
        authorization (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['VirtualMedia']]
    """

    kwargs = _get_kwargs(
        startfrom=startfrom,
        count=count,
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    startfrom: Union[Unset, str] = UNSET,
    count: Union[Unset, int] = UNSET,
    authorization: Union[Unset, str] = UNSET,
) -> Optional[list["VirtualMedia"]]:
    """Get a list of virtual media

    Args:
        startfrom (Union[Unset, str]):
        count (Union[Unset, int]):
        authorization (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['VirtualMedia']
    """

    return sync_detailed(
        client=client,
        startfrom=startfrom,
        count=count,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    startfrom: Union[Unset, str] = UNSET,
    count: Union[Unset, int] = UNSET,
    authorization: Union[Unset, str] = UNSET,
) -> Response[list["VirtualMedia"]]:
    """Get a list of virtual media

    Args:
        startfrom (Union[Unset, str]):
        count (Union[Unset, int]):
        authorization (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['VirtualMedia']]
    """

    kwargs = _get_kwargs(
        startfrom=startfrom,
        count=count,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    startfrom: Union[Unset, str] = UNSET,
    count: Union[Unset, int] = UNSET,
    authorization: Union[Unset, str] = UNSET,
) -> Optional[list["VirtualMedia"]]:
    """Get a list of virtual media

    Args:
        startfrom (Union[Unset, str]):
        count (Union[Unset, int]):
        authorization (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['VirtualMedia']
    """

    return (
        await asyncio_detailed(
            client=client,
            startfrom=startfrom,
            count=count,
            authorization=authorization,
        )
    ).parsed
