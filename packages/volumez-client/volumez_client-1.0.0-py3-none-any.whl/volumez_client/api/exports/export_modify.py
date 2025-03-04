from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.export_modify import ExportModify
from ...models.success_job_response import SuccessJobResponse
from ...types import Response


def _get_kwargs(
    export: str,
    *,
    body: ExportModify,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": f"/exports/{export}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
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
    body: ExportModify,
) -> Response[SuccessJobResponse]:
    """Modify an export

    Args:
        export (str):
        body (ExportModify):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SuccessJobResponse]
    """

    kwargs = _get_kwargs(
        export=export,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    export: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ExportModify,
) -> Optional[SuccessJobResponse]:
    """Modify an export

    Args:
        export (str):
        body (ExportModify):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SuccessJobResponse
    """

    return sync_detailed(
        export=export,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    export: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ExportModify,
) -> Response[SuccessJobResponse]:
    """Modify an export

    Args:
        export (str):
        body (ExportModify):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SuccessJobResponse]
    """

    kwargs = _get_kwargs(
        export=export,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    export: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ExportModify,
) -> Optional[SuccessJobResponse]:
    """Modify an export

    Args:
        export (str):
        body (ExportModify):

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
            body=body,
        )
    ).parsed
