from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.tenant_host_delete_response import TenantHostDeleteResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    tenant_id: str,
    tenant_host: str,
    *,
    authorization: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": f"/tenant/{tenant_id}/tenanthosts/{tenant_host}",
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[TenantHostDeleteResponse]:
    if response.status_code == 200:
        response_200 = TenantHostDeleteResponse.from_dict(response.json())

        return response_200
    if response.status_code == 500:
        response_500 = TenantHostDeleteResponse.from_dict(response.json())

        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[TenantHostDeleteResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    tenant_id: str,
    tenant_host: str,
    *,
    client: Union[AuthenticatedClient, Client],
    authorization: Union[Unset, str] = UNSET,
) -> Response[TenantHostDeleteResponse]:
    """Delete a tenant host

    Args:
        tenant_id (str):
        tenant_host (str):
        authorization (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[TenantHostDeleteResponse]
    """

    kwargs = _get_kwargs(
        tenant_id=tenant_id,
        tenant_host=tenant_host,
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    tenant_id: str,
    tenant_host: str,
    *,
    client: Union[AuthenticatedClient, Client],
    authorization: Union[Unset, str] = UNSET,
) -> Optional[TenantHostDeleteResponse]:
    """Delete a tenant host

    Args:
        tenant_id (str):
        tenant_host (str):
        authorization (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        TenantHostDeleteResponse
    """

    return sync_detailed(
        tenant_id=tenant_id,
        tenant_host=tenant_host,
        client=client,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    tenant_id: str,
    tenant_host: str,
    *,
    client: Union[AuthenticatedClient, Client],
    authorization: Union[Unset, str] = UNSET,
) -> Response[TenantHostDeleteResponse]:
    """Delete a tenant host

    Args:
        tenant_id (str):
        tenant_host (str):
        authorization (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[TenantHostDeleteResponse]
    """

    kwargs = _get_kwargs(
        tenant_id=tenant_id,
        tenant_host=tenant_host,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    tenant_id: str,
    tenant_host: str,
    *,
    client: Union[AuthenticatedClient, Client],
    authorization: Union[Unset, str] = UNSET,
) -> Optional[TenantHostDeleteResponse]:
    """Delete a tenant host

    Args:
        tenant_id (str):
        tenant_host (str):
        authorization (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        TenantHostDeleteResponse
    """

    return (
        await asyncio_detailed(
            tenant_id=tenant_id,
            tenant_host=tenant_host,
            client=client,
            authorization=authorization,
        )
    ).parsed
