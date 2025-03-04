# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from raccoonai import RaccoonAI, AsyncRaccoonAI
from tests.utils import assert_matches_type
from raccoonai.types.tail import AuthStatusResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAuth:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_status(self, client: RaccoonAI) -> None:
        auth = client.tail.auth.status(
            app_name="appName",
            raccoon_passcode="raccoonPasscode",
        )
        assert_matches_type(AuthStatusResponse, auth, path=["response"])

    @parametrize
    def test_raw_response_status(self, client: RaccoonAI) -> None:
        response = client.tail.auth.with_raw_response.status(
            app_name="appName",
            raccoon_passcode="raccoonPasscode",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = response.parse()
        assert_matches_type(AuthStatusResponse, auth, path=["response"])

    @parametrize
    def test_streaming_response_status(self, client: RaccoonAI) -> None:
        with client.tail.auth.with_streaming_response.status(
            app_name="appName",
            raccoon_passcode="raccoonPasscode",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = response.parse()
            assert_matches_type(AuthStatusResponse, auth, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncAuth:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_status(self, async_client: AsyncRaccoonAI) -> None:
        auth = await async_client.tail.auth.status(
            app_name="appName",
            raccoon_passcode="raccoonPasscode",
        )
        assert_matches_type(AuthStatusResponse, auth, path=["response"])

    @parametrize
    async def test_raw_response_status(self, async_client: AsyncRaccoonAI) -> None:
        response = await async_client.tail.auth.with_raw_response.status(
            app_name="appName",
            raccoon_passcode="raccoonPasscode",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = await response.parse()
        assert_matches_type(AuthStatusResponse, auth, path=["response"])

    @parametrize
    async def test_streaming_response_status(self, async_client: AsyncRaccoonAI) -> None:
        async with async_client.tail.auth.with_streaming_response.status(
            app_name="appName",
            raccoon_passcode="raccoonPasscode",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = await response.parse()
            assert_matches_type(AuthStatusResponse, auth, path=["response"])

        assert cast(Any, response.is_closed) is True
