from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_tenant_host_response import GetTenantHostResponse
from ...types import Response


def _get_kwargs(
    *,
    tenanthosttoken: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["tenanthosttoken"] = tenanthosttoken

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/tenant/tenanthost",
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[GetTenantHostResponse]:
    if response.status_code == 200:
        response_200 = GetTenantHostResponse.from_dict(response.json())

        return response_200
    if response.status_code == 500:
        response_500 = GetTenantHostResponse.from_dict(response.json())

        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[GetTenantHostResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    tenanthosttoken: str,
) -> Response[GetTenantHostResponse]:
    """Get a tenant host

    Args:
        tenanthosttoken (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetTenantHostResponse]
    """

    kwargs = _get_kwargs(
        tenanthosttoken=tenanthosttoken,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    tenanthosttoken: str,
) -> Optional[GetTenantHostResponse]:
    """Get a tenant host

    Args:
        tenanthosttoken (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetTenantHostResponse
    """

    return sync_detailed(
        client=client,
        tenanthosttoken=tenanthosttoken,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    tenanthosttoken: str,
) -> Response[GetTenantHostResponse]:
    """Get a tenant host

    Args:
        tenanthosttoken (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetTenantHostResponse]
    """

    kwargs = _get_kwargs(
        tenanthosttoken=tenanthosttoken,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    tenanthosttoken: str,
) -> Optional[GetTenantHostResponse]:
    """Get a tenant host

    Args:
        tenanthosttoken (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetTenantHostResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            tenanthosttoken=tenanthosttoken,
        )
    ).parsed
