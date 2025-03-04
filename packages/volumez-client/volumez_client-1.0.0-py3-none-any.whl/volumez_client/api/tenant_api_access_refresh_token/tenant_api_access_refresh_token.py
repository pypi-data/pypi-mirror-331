from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.refresh_token_response import RefreshTokenResponse
from ...types import Response


def _get_kwargs(
    *,
    refreshtoken: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["refreshtoken"] = refreshtoken

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/tenant/apiaccess/credentials/refresh",
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ErrorResponse, RefreshTokenResponse]]:
    if response.status_code == 200:
        response_200 = RefreshTokenResponse.from_dict(response.json())

        return response_200
    if response.status_code == 500:
        response_500 = ErrorResponse.from_dict(response.json())

        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[ErrorResponse, RefreshTokenResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    refreshtoken: str,
) -> Response[Union[ErrorResponse, RefreshTokenResponse]]:
    """Given the Tenant's API Access Refresh Token, return new Access Token, Identity Token and a newer
    Refresh Token

    Args:
        refreshtoken (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, RefreshTokenResponse]]
    """

    kwargs = _get_kwargs(
        refreshtoken=refreshtoken,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    refreshtoken: str,
) -> Optional[Union[ErrorResponse, RefreshTokenResponse]]:
    """Given the Tenant's API Access Refresh Token, return new Access Token, Identity Token and a newer
    Refresh Token

    Args:
        refreshtoken (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, RefreshTokenResponse]
    """

    return sync_detailed(
        client=client,
        refreshtoken=refreshtoken,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    refreshtoken: str,
) -> Response[Union[ErrorResponse, RefreshTokenResponse]]:
    """Given the Tenant's API Access Refresh Token, return new Access Token, Identity Token and a newer
    Refresh Token

    Args:
        refreshtoken (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, RefreshTokenResponse]]
    """

    kwargs = _get_kwargs(
        refreshtoken=refreshtoken,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    refreshtoken: str,
) -> Optional[Union[ErrorResponse, RefreshTokenResponse]]:
    """Given the Tenant's API Access Refresh Token, return new Access Token, Identity Token and a newer
    Refresh Token

    Args:
        refreshtoken (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, RefreshTokenResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            refreshtoken=refreshtoken,
        )
    ).parsed
