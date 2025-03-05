# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal

import httpx

from .apps import (
    AppsResource,
    AsyncAppsResource,
    AppsResourceWithRawResponse,
    AsyncAppsResourceWithRawResponse,
    AppsResourceWithStreamingResponse,
    AsyncAppsResourceWithStreamingResponse,
)
from .auth import (
    AuthResource,
    AsyncAuthResource,
    AuthResourceWithRawResponse,
    AsyncAuthResourceWithRawResponse,
    AuthResourceWithStreamingResponse,
    AsyncAuthResourceWithStreamingResponse,
)
from ...types import tail_users_params
from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import (
    maybe_transform,
    async_maybe_transform,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.tail_users_response import TailUsersResponse

__all__ = ["TailResource", "AsyncTailResource"]


class TailResource(SyncAPIResource):
    @cached_property
    def apps(self) -> AppsResource:
        return AppsResource(self._client)

    @cached_property
    def auth(self) -> AuthResource:
        return AuthResource(self._client)

    @cached_property
    def with_raw_response(self) -> TailResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/raccoonaihq/raccoonai-python#accessing-raw-response-data-eg-headers
        """
        return TailResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TailResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/raccoonaihq/raccoonai-python#with_streaming_response
        """
        return TailResourceWithStreamingResponse(self)

    def users(
        self,
        *,
        email_id: Optional[str] | NotGiven = NOT_GIVEN,
        limit: Optional[int] | NotGiven = NOT_GIVEN,
        page: Optional[int] | NotGiven = NOT_GIVEN,
        raccoon_passcode: Optional[str] | NotGiven = NOT_GIVEN,
        search_query: Optional[str] | NotGiven = NOT_GIVEN,
        sort_by: Optional[Literal["createdAt", "name", "email", "raccoonPasscode"]] | NotGiven = NOT_GIVEN,
        sort_order: Optional[Literal["ascend", "descend"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TailUsersResponse:
        """
        Get Users Endpoint

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/tail/users",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "email_id": email_id,
                        "limit": limit,
                        "page": page,
                        "raccoon_passcode": raccoon_passcode,
                        "search_query": search_query,
                        "sort_by": sort_by,
                        "sort_order": sort_order,
                    },
                    tail_users_params.TailUsersParams,
                ),
            ),
            cast_to=TailUsersResponse,
        )


class AsyncTailResource(AsyncAPIResource):
    @cached_property
    def apps(self) -> AsyncAppsResource:
        return AsyncAppsResource(self._client)

    @cached_property
    def auth(self) -> AsyncAuthResource:
        return AsyncAuthResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncTailResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/raccoonaihq/raccoonai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncTailResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTailResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/raccoonaihq/raccoonai-python#with_streaming_response
        """
        return AsyncTailResourceWithStreamingResponse(self)

    async def users(
        self,
        *,
        email_id: Optional[str] | NotGiven = NOT_GIVEN,
        limit: Optional[int] | NotGiven = NOT_GIVEN,
        page: Optional[int] | NotGiven = NOT_GIVEN,
        raccoon_passcode: Optional[str] | NotGiven = NOT_GIVEN,
        search_query: Optional[str] | NotGiven = NOT_GIVEN,
        sort_by: Optional[Literal["createdAt", "name", "email", "raccoonPasscode"]] | NotGiven = NOT_GIVEN,
        sort_order: Optional[Literal["ascend", "descend"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TailUsersResponse:
        """
        Get Users Endpoint

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/tail/users",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "email_id": email_id,
                        "limit": limit,
                        "page": page,
                        "raccoon_passcode": raccoon_passcode,
                        "search_query": search_query,
                        "sort_by": sort_by,
                        "sort_order": sort_order,
                    },
                    tail_users_params.TailUsersParams,
                ),
            ),
            cast_to=TailUsersResponse,
        )


class TailResourceWithRawResponse:
    def __init__(self, tail: TailResource) -> None:
        self._tail = tail

        self.users = to_raw_response_wrapper(
            tail.users,
        )

    @cached_property
    def apps(self) -> AppsResourceWithRawResponse:
        return AppsResourceWithRawResponse(self._tail.apps)

    @cached_property
    def auth(self) -> AuthResourceWithRawResponse:
        return AuthResourceWithRawResponse(self._tail.auth)


class AsyncTailResourceWithRawResponse:
    def __init__(self, tail: AsyncTailResource) -> None:
        self._tail = tail

        self.users = async_to_raw_response_wrapper(
            tail.users,
        )

    @cached_property
    def apps(self) -> AsyncAppsResourceWithRawResponse:
        return AsyncAppsResourceWithRawResponse(self._tail.apps)

    @cached_property
    def auth(self) -> AsyncAuthResourceWithRawResponse:
        return AsyncAuthResourceWithRawResponse(self._tail.auth)


class TailResourceWithStreamingResponse:
    def __init__(self, tail: TailResource) -> None:
        self._tail = tail

        self.users = to_streamed_response_wrapper(
            tail.users,
        )

    @cached_property
    def apps(self) -> AppsResourceWithStreamingResponse:
        return AppsResourceWithStreamingResponse(self._tail.apps)

    @cached_property
    def auth(self) -> AuthResourceWithStreamingResponse:
        return AuthResourceWithStreamingResponse(self._tail.auth)


class AsyncTailResourceWithStreamingResponse:
    def __init__(self, tail: AsyncTailResource) -> None:
        self._tail = tail

        self.users = async_to_streamed_response_wrapper(
            tail.users,
        )

    @cached_property
    def apps(self) -> AsyncAppsResourceWithStreamingResponse:
        return AsyncAppsResourceWithStreamingResponse(self._tail.apps)

    @cached_property
    def auth(self) -> AsyncAuthResourceWithStreamingResponse:
        return AsyncAuthResourceWithStreamingResponse(self._tail.auth)
