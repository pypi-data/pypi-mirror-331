from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.policy import Policy
from ...types import UNSET, Response, Unset


def _get_kwargs(
    policy: str,
    *,
    authorization: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/policies/{policy}",
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Policy]:
    if response.status_code == 200:
        response_200 = Policy.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Policy]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    policy: str,
    *,
    client: Union[AuthenticatedClient, Client],
    authorization: Union[Unset, str] = UNSET,
) -> Response[Policy]:
    """Get the properties of a policy

    Args:
        policy (str):
        authorization (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Policy]
    """

    kwargs = _get_kwargs(
        policy=policy,
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    policy: str,
    *,
    client: Union[AuthenticatedClient, Client],
    authorization: Union[Unset, str] = UNSET,
) -> Optional[Policy]:
    """Get the properties of a policy

    Args:
        policy (str):
        authorization (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Policy
    """

    return sync_detailed(
        policy=policy,
        client=client,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    policy: str,
    *,
    client: Union[AuthenticatedClient, Client],
    authorization: Union[Unset, str] = UNSET,
) -> Response[Policy]:
    """Get the properties of a policy

    Args:
        policy (str):
        authorization (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Policy]
    """

    kwargs = _get_kwargs(
        policy=policy,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    policy: str,
    *,
    client: Union[AuthenticatedClient, Client],
    authorization: Union[Unset, str] = UNSET,
) -> Optional[Policy]:
    """Get the properties of a policy

    Args:
        policy (str):
        authorization (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Policy
    """

    return (
        await asyncio_detailed(
            policy=policy,
            client=client,
            authorization=authorization,
        )
    ).parsed
