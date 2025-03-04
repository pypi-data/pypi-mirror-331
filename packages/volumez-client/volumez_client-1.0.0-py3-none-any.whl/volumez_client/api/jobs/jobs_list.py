from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.job import Job
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    internal: Union[Unset, bool] = UNSET,
    page: Union[Unset, int] = UNSET,
    count: Union[Unset, int] = UNSET,
    authorization: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    params: dict[str, Any] = {}

    params["internal"] = internal

    params["page"] = page

    params["count"] = count

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/jobs",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[list["Job"]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Job.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[list["Job"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    internal: Union[Unset, bool] = UNSET,
    page: Union[Unset, int] = UNSET,
    count: Union[Unset, int] = UNSET,
    authorization: Union[Unset, str] = UNSET,
) -> Response[list["Job"]]:
    """Get a list of jobs

    Args:
        internal (Union[Unset, bool]):
        page (Union[Unset, int]):
        count (Union[Unset, int]):
        authorization (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['Job']]
    """

    kwargs = _get_kwargs(
        internal=internal,
        page=page,
        count=count,
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    internal: Union[Unset, bool] = UNSET,
    page: Union[Unset, int] = UNSET,
    count: Union[Unset, int] = UNSET,
    authorization: Union[Unset, str] = UNSET,
) -> Optional[list["Job"]]:
    """Get a list of jobs

    Args:
        internal (Union[Unset, bool]):
        page (Union[Unset, int]):
        count (Union[Unset, int]):
        authorization (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['Job']
    """

    return sync_detailed(
        client=client,
        internal=internal,
        page=page,
        count=count,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    internal: Union[Unset, bool] = UNSET,
    page: Union[Unset, int] = UNSET,
    count: Union[Unset, int] = UNSET,
    authorization: Union[Unset, str] = UNSET,
) -> Response[list["Job"]]:
    """Get a list of jobs

    Args:
        internal (Union[Unset, bool]):
        page (Union[Unset, int]):
        count (Union[Unset, int]):
        authorization (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['Job']]
    """

    kwargs = _get_kwargs(
        internal=internal,
        page=page,
        count=count,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    internal: Union[Unset, bool] = UNSET,
    page: Union[Unset, int] = UNSET,
    count: Union[Unset, int] = UNSET,
    authorization: Union[Unset, str] = UNSET,
) -> Optional[list["Job"]]:
    """Get a list of jobs

    Args:
        internal (Union[Unset, bool]):
        page (Union[Unset, int]):
        count (Union[Unset, int]):
        authorization (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['Job']
    """

    return (
        await asyncio_detailed(
            client=client,
            internal=internal,
            page=page,
            count=count,
            authorization=authorization,
        )
    ).parsed
