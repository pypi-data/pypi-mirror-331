# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from raccoonai import RaccoonAI, AsyncRaccoonAI
from tests.utils import assert_matches_type
from raccoonai.types import TailUsersResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTail:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_users(self, client: RaccoonAI) -> None:
        tail = client.tail.users()
        assert_matches_type(TailUsersResponse, tail, path=["response"])

    @parametrize
    def test_method_users_with_all_params(self, client: RaccoonAI) -> None:
        tail = client.tail.users(
            email_id="emailId",
            limit=1,
            page=1,
            raccoon_passcode="raccoonPasscode",
            search_query="searchQuery",
            sort_by="createdAt",
            sort_order="ascend",
        )
        assert_matches_type(TailUsersResponse, tail, path=["response"])

    @parametrize
    def test_raw_response_users(self, client: RaccoonAI) -> None:
        response = client.tail.with_raw_response.users()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        tail = response.parse()
        assert_matches_type(TailUsersResponse, tail, path=["response"])

    @parametrize
    def test_streaming_response_users(self, client: RaccoonAI) -> None:
        with client.tail.with_streaming_response.users() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            tail = response.parse()
            assert_matches_type(TailUsersResponse, tail, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncTail:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_users(self, async_client: AsyncRaccoonAI) -> None:
        tail = await async_client.tail.users()
        assert_matches_type(TailUsersResponse, tail, path=["response"])

    @parametrize
    async def test_method_users_with_all_params(self, async_client: AsyncRaccoonAI) -> None:
        tail = await async_client.tail.users(
            email_id="emailId",
            limit=1,
            page=1,
            raccoon_passcode="raccoonPasscode",
            search_query="searchQuery",
            sort_by="createdAt",
            sort_order="ascend",
        )
        assert_matches_type(TailUsersResponse, tail, path=["response"])

    @parametrize
    async def test_raw_response_users(self, async_client: AsyncRaccoonAI) -> None:
        response = await async_client.tail.with_raw_response.users()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        tail = await response.parse()
        assert_matches_type(TailUsersResponse, tail, path=["response"])

    @parametrize
    async def test_streaming_response_users(self, async_client: AsyncRaccoonAI) -> None:
        async with async_client.tail.with_streaming_response.users() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            tail = await response.parse()
            assert_matches_type(TailUsersResponse, tail, path=["response"])

        assert cast(Any, response.is_closed) is True
