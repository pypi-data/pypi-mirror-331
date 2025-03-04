from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.regular_response import RegularResponse
from ...models.volume import Volume
from ...types import UNSET, Response, Unset


def _get_kwargs(
    volume: str,
    *,
    body: Volume,
    authorization: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": f"/volumes/{volume}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

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
    volume: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Volume,
    authorization: Union[Unset, str] = UNSET,
) -> Response[RegularResponse]:
    """Modify a volume

    Args:
        volume (str):
        authorization (Union[Unset, str]):
        body (Volume):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RegularResponse]
    """

    kwargs = _get_kwargs(
        volume=volume,
        body=body,
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    volume: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Volume,
    authorization: Union[Unset, str] = UNSET,
) -> Optional[RegularResponse]:
    """Modify a volume

    Args:
        volume (str):
        authorization (Union[Unset, str]):
        body (Volume):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RegularResponse
    """

    return sync_detailed(
        volume=volume,
        client=client,
        body=body,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    volume: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Volume,
    authorization: Union[Unset, str] = UNSET,
) -> Response[RegularResponse]:
    """Modify a volume

    Args:
        volume (str):
        authorization (Union[Unset, str]):
        body (Volume):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RegularResponse]
    """

    kwargs = _get_kwargs(
        volume=volume,
        body=body,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    volume: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Volume,
    authorization: Union[Unset, str] = UNSET,
) -> Optional[RegularResponse]:
    """Modify a volume

    Args:
        volume (str):
        authorization (Union[Unset, str]):
        body (Volume):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RegularResponse
    """

    return (
        await asyncio_detailed(
            volume=volume,
            client=client,
            body=body,
            authorization=authorization,
        )
    ).parsed
