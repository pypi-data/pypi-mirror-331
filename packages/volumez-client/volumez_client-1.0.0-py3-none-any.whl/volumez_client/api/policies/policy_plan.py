from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.plan import Plan
from ...types import UNSET, Response, Unset


def _get_kwargs(
    policy: str,
    size: int,
    zone: str,
    *,
    capacity_group: Union[Unset, str] = UNSET,
    authorization: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    params: dict[str, Any] = {}

    params["capacity_group"] = capacity_group

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/policies/{policy}/size/{size}/zone/{zone}",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ErrorResponse, Plan]]:
    if response.status_code == 200:
        response_200 = Plan.from_dict(response.json())

        return response_200
    if response.status_code == 404:
        response_404 = ErrorResponse.from_dict(response.json())

        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[ErrorResponse, Plan]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    policy: str,
    size: int,
    zone: str,
    *,
    client: Union[AuthenticatedClient, Client],
    capacity_group: Union[Unset, str] = UNSET,
    authorization: Union[Unset, str] = UNSET,
) -> Response[Union[ErrorResponse, Plan]]:
    """Show policy volume create plan

    Args:
        policy (str):
        size (int):
        zone (str):
        capacity_group (Union[Unset, str]):
        authorization (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, Plan]]
    """

    kwargs = _get_kwargs(
        policy=policy,
        size=size,
        zone=zone,
        capacity_group=capacity_group,
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    policy: str,
    size: int,
    zone: str,
    *,
    client: Union[AuthenticatedClient, Client],
    capacity_group: Union[Unset, str] = UNSET,
    authorization: Union[Unset, str] = UNSET,
) -> Optional[Union[ErrorResponse, Plan]]:
    """Show policy volume create plan

    Args:
        policy (str):
        size (int):
        zone (str):
        capacity_group (Union[Unset, str]):
        authorization (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, Plan]
    """

    return sync_detailed(
        policy=policy,
        size=size,
        zone=zone,
        client=client,
        capacity_group=capacity_group,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    policy: str,
    size: int,
    zone: str,
    *,
    client: Union[AuthenticatedClient, Client],
    capacity_group: Union[Unset, str] = UNSET,
    authorization: Union[Unset, str] = UNSET,
) -> Response[Union[ErrorResponse, Plan]]:
    """Show policy volume create plan

    Args:
        policy (str):
        size (int):
        zone (str):
        capacity_group (Union[Unset, str]):
        authorization (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, Plan]]
    """

    kwargs = _get_kwargs(
        policy=policy,
        size=size,
        zone=zone,
        capacity_group=capacity_group,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    policy: str,
    size: int,
    zone: str,
    *,
    client: Union[AuthenticatedClient, Client],
    capacity_group: Union[Unset, str] = UNSET,
    authorization: Union[Unset, str] = UNSET,
) -> Optional[Union[ErrorResponse, Plan]]:
    """Show policy volume create plan

    Args:
        policy (str):
        size (int):
        zone (str):
        capacity_group (Union[Unset, str]):
        authorization (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, Plan]
    """

    return (
        await asyncio_detailed(
            policy=policy,
            size=size,
            zone=zone,
            client=client,
            capacity_group=capacity_group,
            authorization=authorization,
        )
    ).parsed
