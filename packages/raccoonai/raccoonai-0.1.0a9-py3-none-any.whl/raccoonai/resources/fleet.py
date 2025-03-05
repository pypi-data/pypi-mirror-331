# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Literal

import httpx

from ..types import fleet_create_params, fleet_sessions_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import (
    maybe_transform,
    async_maybe_transform,
)
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.fleet_logs_response import FleetLogsResponse
from ..types.fleet_create_response import FleetCreateResponse
from ..types.fleet_status_response import FleetStatusResponse
from ..types.fleet_sessions_response import FleetSessionsResponse
from ..types.fleet_terminate_response import FleetTerminateResponse

__all__ = ["FleetResource", "AsyncFleetResource"]


class FleetResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FleetResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/raccoonaihq/raccoonai-python#accessing-raw-response-data-eg-headers
        """
        return FleetResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FleetResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/raccoonaihq/raccoonai-python#with_streaming_response
        """
        return FleetResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        advanced: Optional[fleet_create_params.Advanced] | NotGiven = NOT_GIVEN,
        browser_type: Optional[Literal["chromium", "firefox", "webkit"]] | NotGiven = NOT_GIVEN,
        headless: Optional[bool] | NotGiven = NOT_GIVEN,
        raccoon_passcode: Optional[str] | NotGiven = NOT_GIVEN,
        session_timeout: Optional[int] | NotGiven = NOT_GIVEN,
        settings: Optional[fleet_create_params.Settings] | NotGiven = NOT_GIVEN,
        url: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FleetCreateResponse:
        """
        Fleet Websocket Session Create Endpoint

        Args:
          advanced: Advanced configuration options for the session, such as ad-blocking and CAPTCHA
              solving.

          browser_type: The type of browser to use. Supported values include 'chromium', 'firefox', and
              'webkit'.

          headless: Whether to run the browser in headless mode.

          raccoon_passcode: The raccoon passcode associated with the end user on behalf of which the call is
              being made if any.

          session_timeout: The timeout for the browser session in seconds.

          settings: Configuration settings for the browser, such as viewport size and User-Agent
              string.

          url: The entrypoint url for the session.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/sessions/create",
            body=maybe_transform(
                {
                    "advanced": advanced,
                    "browser_type": browser_type,
                    "headless": headless,
                    "raccoon_passcode": raccoon_passcode,
                    "session_timeout": session_timeout,
                    "settings": settings,
                    "url": url,
                },
                fleet_create_params.FleetCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FleetCreateResponse,
        )

    def logs(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FleetLogsResponse:
        """
        Fleet Session Logs Endpoint

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return self._get(
            f"/sessions/{session_id}/logs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FleetLogsResponse,
        )

    def sessions(
        self,
        *,
        end_time: Optional[int] | NotGiven = NOT_GIVEN,
        execution_type: Optional[List[Literal["run", "extract", "fleet"]]] | NotGiven = NOT_GIVEN,
        limit: Optional[int] | NotGiven = NOT_GIVEN,
        page: Optional[int] | NotGiven = NOT_GIVEN,
        raccoon_passcode: Optional[str] | NotGiven = NOT_GIVEN,
        session_id: Optional[str] | NotGiven = NOT_GIVEN,
        sort_by: Optional[Literal["timestamp", "executionTime", "taskId", "status", "executionType"]]
        | NotGiven = NOT_GIVEN,
        sort_order: Optional[Literal["ascend", "descend"]] | NotGiven = NOT_GIVEN,
        start_time: Optional[int] | NotGiven = NOT_GIVEN,
        task_id: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FleetSessionsResponse:
        """
        Get Sessions Endpoint

        Args:
          end_time: Filter sessions created before this Unix timestamp (in milliseconds).

          execution_type: Filter sessions by execution type (e.g., 'run', 'extract').

          limit: Number of sessions per page (maximum 100).

          page: Page number for pagination.

          raccoon_passcode: Filter sessions by Raccoon passcode.

          session_id: Filter sessions by a specific session ID.

          sort_by: Field to sort sessions by (e.g., 'timestamp', 'executionTime').

          sort_order: Sort order ('ascend' or 'descend').

          start_time: Filter sessions created after this Unix timestamp (in milliseconds).

          task_id: Filter sessions by a specific task ID.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/sessions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "end_time": end_time,
                        "execution_type": execution_type,
                        "limit": limit,
                        "page": page,
                        "raccoon_passcode": raccoon_passcode,
                        "session_id": session_id,
                        "sort_by": sort_by,
                        "sort_order": sort_order,
                        "start_time": start_time,
                        "task_id": task_id,
                    },
                    fleet_sessions_params.FleetSessionsParams,
                ),
            ),
            cast_to=FleetSessionsResponse,
        )

    def status(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FleetStatusResponse:
        """
        Fleet Session Status Endpoint

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return self._get(
            f"/sessions/{session_id}/status",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FleetStatusResponse,
        )

    def terminate(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FleetTerminateResponse:
        """
        Fleet Session Terminate Endpoint

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return self._delete(
            f"/sessions/{session_id}/terminate",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FleetTerminateResponse,
        )


class AsyncFleetResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFleetResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/raccoonaihq/raccoonai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncFleetResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFleetResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/raccoonaihq/raccoonai-python#with_streaming_response
        """
        return AsyncFleetResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        advanced: Optional[fleet_create_params.Advanced] | NotGiven = NOT_GIVEN,
        browser_type: Optional[Literal["chromium", "firefox", "webkit"]] | NotGiven = NOT_GIVEN,
        headless: Optional[bool] | NotGiven = NOT_GIVEN,
        raccoon_passcode: Optional[str] | NotGiven = NOT_GIVEN,
        session_timeout: Optional[int] | NotGiven = NOT_GIVEN,
        settings: Optional[fleet_create_params.Settings] | NotGiven = NOT_GIVEN,
        url: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FleetCreateResponse:
        """
        Fleet Websocket Session Create Endpoint

        Args:
          advanced: Advanced configuration options for the session, such as ad-blocking and CAPTCHA
              solving.

          browser_type: The type of browser to use. Supported values include 'chromium', 'firefox', and
              'webkit'.

          headless: Whether to run the browser in headless mode.

          raccoon_passcode: The raccoon passcode associated with the end user on behalf of which the call is
              being made if any.

          session_timeout: The timeout for the browser session in seconds.

          settings: Configuration settings for the browser, such as viewport size and User-Agent
              string.

          url: The entrypoint url for the session.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/sessions/create",
            body=await async_maybe_transform(
                {
                    "advanced": advanced,
                    "browser_type": browser_type,
                    "headless": headless,
                    "raccoon_passcode": raccoon_passcode,
                    "session_timeout": session_timeout,
                    "settings": settings,
                    "url": url,
                },
                fleet_create_params.FleetCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FleetCreateResponse,
        )

    async def logs(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FleetLogsResponse:
        """
        Fleet Session Logs Endpoint

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return await self._get(
            f"/sessions/{session_id}/logs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FleetLogsResponse,
        )

    async def sessions(
        self,
        *,
        end_time: Optional[int] | NotGiven = NOT_GIVEN,
        execution_type: Optional[List[Literal["run", "extract", "fleet"]]] | NotGiven = NOT_GIVEN,
        limit: Optional[int] | NotGiven = NOT_GIVEN,
        page: Optional[int] | NotGiven = NOT_GIVEN,
        raccoon_passcode: Optional[str] | NotGiven = NOT_GIVEN,
        session_id: Optional[str] | NotGiven = NOT_GIVEN,
        sort_by: Optional[Literal["timestamp", "executionTime", "taskId", "status", "executionType"]]
        | NotGiven = NOT_GIVEN,
        sort_order: Optional[Literal["ascend", "descend"]] | NotGiven = NOT_GIVEN,
        start_time: Optional[int] | NotGiven = NOT_GIVEN,
        task_id: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FleetSessionsResponse:
        """
        Get Sessions Endpoint

        Args:
          end_time: Filter sessions created before this Unix timestamp (in milliseconds).

          execution_type: Filter sessions by execution type (e.g., 'run', 'extract').

          limit: Number of sessions per page (maximum 100).

          page: Page number for pagination.

          raccoon_passcode: Filter sessions by Raccoon passcode.

          session_id: Filter sessions by a specific session ID.

          sort_by: Field to sort sessions by (e.g., 'timestamp', 'executionTime').

          sort_order: Sort order ('ascend' or 'descend').

          start_time: Filter sessions created after this Unix timestamp (in milliseconds).

          task_id: Filter sessions by a specific task ID.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/sessions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "end_time": end_time,
                        "execution_type": execution_type,
                        "limit": limit,
                        "page": page,
                        "raccoon_passcode": raccoon_passcode,
                        "session_id": session_id,
                        "sort_by": sort_by,
                        "sort_order": sort_order,
                        "start_time": start_time,
                        "task_id": task_id,
                    },
                    fleet_sessions_params.FleetSessionsParams,
                ),
            ),
            cast_to=FleetSessionsResponse,
        )

    async def status(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FleetStatusResponse:
        """
        Fleet Session Status Endpoint

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return await self._get(
            f"/sessions/{session_id}/status",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FleetStatusResponse,
        )

    async def terminate(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FleetTerminateResponse:
        """
        Fleet Session Terminate Endpoint

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return await self._delete(
            f"/sessions/{session_id}/terminate",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FleetTerminateResponse,
        )


class FleetResourceWithRawResponse:
    def __init__(self, fleet: FleetResource) -> None:
        self._fleet = fleet

        self.create = to_raw_response_wrapper(
            fleet.create,
        )
        self.logs = to_raw_response_wrapper(
            fleet.logs,
        )
        self.sessions = to_raw_response_wrapper(
            fleet.sessions,
        )
        self.status = to_raw_response_wrapper(
            fleet.status,
        )
        self.terminate = to_raw_response_wrapper(
            fleet.terminate,
        )


class AsyncFleetResourceWithRawResponse:
    def __init__(self, fleet: AsyncFleetResource) -> None:
        self._fleet = fleet

        self.create = async_to_raw_response_wrapper(
            fleet.create,
        )
        self.logs = async_to_raw_response_wrapper(
            fleet.logs,
        )
        self.sessions = async_to_raw_response_wrapper(
            fleet.sessions,
        )
        self.status = async_to_raw_response_wrapper(
            fleet.status,
        )
        self.terminate = async_to_raw_response_wrapper(
            fleet.terminate,
        )


class FleetResourceWithStreamingResponse:
    def __init__(self, fleet: FleetResource) -> None:
        self._fleet = fleet

        self.create = to_streamed_response_wrapper(
            fleet.create,
        )
        self.logs = to_streamed_response_wrapper(
            fleet.logs,
        )
        self.sessions = to_streamed_response_wrapper(
            fleet.sessions,
        )
        self.status = to_streamed_response_wrapper(
            fleet.status,
        )
        self.terminate = to_streamed_response_wrapper(
            fleet.terminate,
        )


class AsyncFleetResourceWithStreamingResponse:
    def __init__(self, fleet: AsyncFleetResource) -> None:
        self._fleet = fleet

        self.create = async_to_streamed_response_wrapper(
            fleet.create,
        )
        self.logs = async_to_streamed_response_wrapper(
            fleet.logs,
        )
        self.sessions = async_to_streamed_response_wrapper(
            fleet.sessions,
        )
        self.status = async_to_streamed_response_wrapper(
            fleet.status,
        )
        self.terminate = async_to_streamed_response_wrapper(
            fleet.terminate,
        )
