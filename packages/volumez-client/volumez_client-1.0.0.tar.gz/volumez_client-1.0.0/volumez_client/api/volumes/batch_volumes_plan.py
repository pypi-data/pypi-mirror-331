from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.batch_volumes_plan_body import BatchVolumesPlanBody
from ...models.volume_plan_output import VolumePlanOutput
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: BatchVolumesPlanBody,
    verbose: Union[Unset, bool] = True,
    authorization: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    params: dict[str, Any] = {}

    params["verbose"] = verbose

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/volumes/plan",
        "params": params,
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[VolumePlanOutput]:
    if response.status_code == 200:
        response_200 = VolumePlanOutput.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[VolumePlanOutput]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: BatchVolumesPlanBody,
    verbose: Union[Unset, bool] = True,
    authorization: Union[Unset, str] = UNSET,
) -> Response[VolumePlanOutput]:
    """check if volumes can be created

    Args:
        verbose (Union[Unset, bool]):  Default: True.
        authorization (Union[Unset, str]):
        body (BatchVolumesPlanBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[VolumePlanOutput]
    """

    kwargs = _get_kwargs(
        body=body,
        verbose=verbose,
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: BatchVolumesPlanBody,
    verbose: Union[Unset, bool] = True,
    authorization: Union[Unset, str] = UNSET,
) -> Optional[VolumePlanOutput]:
    """check if volumes can be created

    Args:
        verbose (Union[Unset, bool]):  Default: True.
        authorization (Union[Unset, str]):
        body (BatchVolumesPlanBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        VolumePlanOutput
    """

    return sync_detailed(
        client=client,
        body=body,
        verbose=verbose,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: BatchVolumesPlanBody,
    verbose: Union[Unset, bool] = True,
    authorization: Union[Unset, str] = UNSET,
) -> Response[VolumePlanOutput]:
    """check if volumes can be created

    Args:
        verbose (Union[Unset, bool]):  Default: True.
        authorization (Union[Unset, str]):
        body (BatchVolumesPlanBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[VolumePlanOutput]
    """

    kwargs = _get_kwargs(
        body=body,
        verbose=verbose,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: BatchVolumesPlanBody,
    verbose: Union[Unset, bool] = True,
    authorization: Union[Unset, str] = UNSET,
) -> Optional[VolumePlanOutput]:
    """check if volumes can be created

    Args:
        verbose (Union[Unset, bool]):  Default: True.
        authorization (Union[Unset, str]):
        body (BatchVolumesPlanBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        VolumePlanOutput
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            verbose=verbose,
            authorization=authorization,
        )
    ).parsed
