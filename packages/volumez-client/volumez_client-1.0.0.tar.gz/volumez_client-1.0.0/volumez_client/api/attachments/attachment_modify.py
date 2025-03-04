from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.attachment import Attachment
from ...models.regular_response import RegularResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    volume: str,
    snapshot: str,
    node: str,
    *,
    body: Attachment,
    authorization: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": f"/volumes/{volume}/snapshots/{snapshot}/attachments/{node}",
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
    snapshot: str,
    node: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Attachment,
    authorization: Union[Unset, str] = UNSET,
) -> Response[RegularResponse]:
    """Modify an attachment

    Args:
        volume (str):
        snapshot (str):
        node (str):
        authorization (Union[Unset, str]):
        body (Attachment):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RegularResponse]
    """

    kwargs = _get_kwargs(
        volume=volume,
        snapshot=snapshot,
        node=node,
        body=body,
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    volume: str,
    snapshot: str,
    node: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Attachment,
    authorization: Union[Unset, str] = UNSET,
) -> Optional[RegularResponse]:
    """Modify an attachment

    Args:
        volume (str):
        snapshot (str):
        node (str):
        authorization (Union[Unset, str]):
        body (Attachment):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RegularResponse
    """

    return sync_detailed(
        volume=volume,
        snapshot=snapshot,
        node=node,
        client=client,
        body=body,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    volume: str,
    snapshot: str,
    node: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Attachment,
    authorization: Union[Unset, str] = UNSET,
) -> Response[RegularResponse]:
    """Modify an attachment

    Args:
        volume (str):
        snapshot (str):
        node (str):
        authorization (Union[Unset, str]):
        body (Attachment):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RegularResponse]
    """

    kwargs = _get_kwargs(
        volume=volume,
        snapshot=snapshot,
        node=node,
        body=body,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    volume: str,
    snapshot: str,
    node: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Attachment,
    authorization: Union[Unset, str] = UNSET,
) -> Optional[RegularResponse]:
    """Modify an attachment

    Args:
        volume (str):
        snapshot (str):
        node (str):
        authorization (Union[Unset, str]):
        body (Attachment):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RegularResponse
    """

    return (
        await asyncio_detailed(
            volume=volume,
            snapshot=snapshot,
            node=node,
            client=client,
            body=body,
            authorization=authorization,
        )
    ).parsed
