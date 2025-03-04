from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_tenant_id_response import GetTenantIDResponse
from ...types import Response


def _get_kwargs(
    *,
    tenanttoken: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["tenanttoken"] = tenanttoken

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/tenant/tenantid",
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[GetTenantIDResponse]:
    if response.status_code == 200:
        response_200 = GetTenantIDResponse.from_dict(response.json())

        return response_200
    if response.status_code == 500:
        response_500 = GetTenantIDResponse.from_dict(response.json())

        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[GetTenantIDResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    tenanttoken: str,
) -> Response[GetTenantIDResponse]:
    """Get a Tenant ID from Tenant's Token

    Args:
        tenanttoken (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetTenantIDResponse]
    """

    kwargs = _get_kwargs(
        tenanttoken=tenanttoken,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    tenanttoken: str,
) -> Optional[GetTenantIDResponse]:
    """Get a Tenant ID from Tenant's Token

    Args:
        tenanttoken (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetTenantIDResponse
    """

    return sync_detailed(
        client=client,
        tenanttoken=tenanttoken,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    tenanttoken: str,
) -> Response[GetTenantIDResponse]:
    """Get a Tenant ID from Tenant's Token

    Args:
        tenanttoken (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetTenantIDResponse]
    """

    kwargs = _get_kwargs(
        tenanttoken=tenanttoken,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    tenanttoken: str,
) -> Optional[GetTenantIDResponse]:
    """Get a Tenant ID from Tenant's Token

    Args:
        tenanttoken (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetTenantIDResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            tenanttoken=tenanttoken,
        )
    ).parsed
