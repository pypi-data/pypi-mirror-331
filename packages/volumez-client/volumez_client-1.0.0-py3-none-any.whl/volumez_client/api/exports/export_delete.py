from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.success_job_response import SuccessJobResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    export: str,
    *,
    force: Union[Unset, bool] = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["force"] = force

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": f"/exports/{export}",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[SuccessJobResponse]:
    if response.status_code == 200:
        response_200 = SuccessJobResponse.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[SuccessJobResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    export: str,
    *,
    client: Union[AuthenticatedClient, Client],
    force: Union[Unset, bool] = False,
) -> Response[SuccessJobResponse]:
    """Delete an export

    Args:
        export (str):
        force (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SuccessJobResponse]
    """

    kwargs = _get_kwargs(
        export=export,
        force=force,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    export: str,
    *,
    client: Union[AuthenticatedClient, Client],
    force: Union[Unset, bool] = False,
) -> Optional[SuccessJobResponse]:
    """Delete an export

    Args:
        export (str):
        force (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SuccessJobResponse
    """

    return sync_detailed(
        export=export,
        client=client,
        force=force,
    ).parsed


async def asyncio_detailed(
    export: str,
    *,
    client: Union[AuthenticatedClient, Client],
    force: Union[Unset, bool] = False,
) -> Response[SuccessJobResponse]:
    """Delete an export

    Args:
        export (str):
        force (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SuccessJobResponse]
    """

    kwargs = _get_kwargs(
        export=export,
        force=force,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    export: str,
    *,
    client: Union[AuthenticatedClient, Client],
    force: Union[Unset, bool] = False,
) -> Optional[SuccessJobResponse]:
    """Delete an export

    Args:
        export (str):
        force (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SuccessJobResponse
    """

    return (
        await asyncio_detailed(
            export=export,
            client=client,
            force=force,
        )
    ).parsed
