from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.regular_response import RegularResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    media: str,
    *,
    capacity_group: Union[Unset, str] = UNSET,
    reprofile: Union[Unset, bool] = UNSET,
    block_size: Union[Unset, int] = UNSET,
    authorization: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    params: dict[str, Any] = {}

    params["capacity_group"] = capacity_group

    params["reprofile"] = reprofile

    params["block_size"] = block_size

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": f"/media/{media}/assign",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[RegularResponse]:
    if response.status_code == 200:
        response_200 = RegularResponse.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[RegularResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    media: str,
    *,
    client: Union[AuthenticatedClient, Client],
    capacity_group: Union[Unset, str] = UNSET,
    reprofile: Union[Unset, bool] = UNSET,
    block_size: Union[Unset, int] = UNSET,
    authorization: Union[Unset, str] = UNSET,
) -> Response[RegularResponse]:
    """Assign media

    Args:
        media (str):
        capacity_group (Union[Unset, str]):
        reprofile (Union[Unset, bool]):
        block_size (Union[Unset, int]):
        authorization (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RegularResponse]
    """

    kwargs = _get_kwargs(
        media=media,
        capacity_group=capacity_group,
        reprofile=reprofile,
        block_size=block_size,
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    media: str,
    *,
    client: Union[AuthenticatedClient, Client],
    capacity_group: Union[Unset, str] = UNSET,
    reprofile: Union[Unset, bool] = UNSET,
    block_size: Union[Unset, int] = UNSET,
    authorization: Union[Unset, str] = UNSET,
) -> Optional[RegularResponse]:
    """Assign media

    Args:
        media (str):
        capacity_group (Union[Unset, str]):
        reprofile (Union[Unset, bool]):
        block_size (Union[Unset, int]):
        authorization (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RegularResponse
    """

    return sync_detailed(
        media=media,
        client=client,
        capacity_group=capacity_group,
        reprofile=reprofile,
        block_size=block_size,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    media: str,
    *,
    client: Union[AuthenticatedClient, Client],
    capacity_group: Union[Unset, str] = UNSET,
    reprofile: Union[Unset, bool] = UNSET,
    block_size: Union[Unset, int] = UNSET,
    authorization: Union[Unset, str] = UNSET,
) -> Response[RegularResponse]:
    """Assign media

    Args:
        media (str):
        capacity_group (Union[Unset, str]):
        reprofile (Union[Unset, bool]):
        block_size (Union[Unset, int]):
        authorization (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RegularResponse]
    """

    kwargs = _get_kwargs(
        media=media,
        capacity_group=capacity_group,
        reprofile=reprofile,
        block_size=block_size,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    media: str,
    *,
    client: Union[AuthenticatedClient, Client],
    capacity_group: Union[Unset, str] = UNSET,
    reprofile: Union[Unset, bool] = UNSET,
    block_size: Union[Unset, int] = UNSET,
    authorization: Union[Unset, str] = UNSET,
) -> Optional[RegularResponse]:
    """Assign media

    Args:
        media (str):
        capacity_group (Union[Unset, str]):
        reprofile (Union[Unset, bool]):
        block_size (Union[Unset, int]):
        authorization (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RegularResponse
    """

    return (
        await asyncio_detailed(
            media=media,
            client=client,
            capacity_group=capacity_group,
            reprofile=reprofile,
            block_size=block_size,
            authorization=authorization,
        )
    ).parsed
