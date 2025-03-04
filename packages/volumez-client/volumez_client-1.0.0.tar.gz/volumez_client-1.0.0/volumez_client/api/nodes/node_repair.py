from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.regular_response import RegularResponse
from ...models.repair_cmds import RepairCmds
from ...types import UNSET, Response, Unset


def _get_kwargs(
    node: str,
    tenant: str,
    *,
    body: RepairCmds,
    authorization: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/nodes/repair/{node}/{tenant}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ErrorResponse, RegularResponse]]:
    if response.status_code == 200:
        response_200 = RegularResponse.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = ErrorResponse.from_dict(response.json())

        return response_400
    if response.status_code == 404:
        response_404 = ErrorResponse.from_dict(response.json())

        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[ErrorResponse, RegularResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    node: str,
    tenant: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: RepairCmds,
    authorization: Union[Unset, str] = UNSET,
) -> Response[Union[ErrorResponse, RegularResponse]]:
    """Execute commands on node for repair

    Args:
        node (str):
        tenant (str):
        authorization (Union[Unset, str]):
        body (RepairCmds):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, RegularResponse]]
    """

    kwargs = _get_kwargs(
        node=node,
        tenant=tenant,
        body=body,
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    node: str,
    tenant: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: RepairCmds,
    authorization: Union[Unset, str] = UNSET,
) -> Optional[Union[ErrorResponse, RegularResponse]]:
    """Execute commands on node for repair

    Args:
        node (str):
        tenant (str):
        authorization (Union[Unset, str]):
        body (RepairCmds):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, RegularResponse]
    """

    return sync_detailed(
        node=node,
        tenant=tenant,
        client=client,
        body=body,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    node: str,
    tenant: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: RepairCmds,
    authorization: Union[Unset, str] = UNSET,
) -> Response[Union[ErrorResponse, RegularResponse]]:
    """Execute commands on node for repair

    Args:
        node (str):
        tenant (str):
        authorization (Union[Unset, str]):
        body (RepairCmds):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, RegularResponse]]
    """

    kwargs = _get_kwargs(
        node=node,
        tenant=tenant,
        body=body,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    node: str,
    tenant: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: RepairCmds,
    authorization: Union[Unset, str] = UNSET,
) -> Optional[Union[ErrorResponse, RegularResponse]]:
    """Execute commands on node for repair

    Args:
        node (str):
        tenant (str):
        authorization (Union[Unset, str]):
        body (RepairCmds):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, RegularResponse]
    """

    return (
        await asyncio_detailed(
            node=node,
            tenant=tenant,
            client=client,
            body=body,
            authorization=authorization,
        )
    ).parsed
