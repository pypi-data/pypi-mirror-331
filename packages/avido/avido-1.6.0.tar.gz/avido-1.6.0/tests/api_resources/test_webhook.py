# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from avido import Avido, AsyncAvido
from avido.types import WebhookValidateResponse
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestWebhook:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_validate(self, client: Avido) -> None:
        webhook = client.webhook.validate(
            body={},
            signature="signature",
            timestamp=1687802842609,
        )
        assert_matches_type(WebhookValidateResponse, webhook, path=["response"])

    @parametrize
    def test_raw_response_validate(self, client: Avido) -> None:
        response = client.webhook.with_raw_response.validate(
            body={},
            signature="signature",
            timestamp=1687802842609,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook = response.parse()
        assert_matches_type(WebhookValidateResponse, webhook, path=["response"])

    @parametrize
    def test_streaming_response_validate(self, client: Avido) -> None:
        with client.webhook.with_streaming_response.validate(
            body={},
            signature="signature",
            timestamp=1687802842609,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook = response.parse()
            assert_matches_type(WebhookValidateResponse, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncWebhook:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_validate(self, async_client: AsyncAvido) -> None:
        webhook = await async_client.webhook.validate(
            body={},
            signature="signature",
            timestamp=1687802842609,
        )
        assert_matches_type(WebhookValidateResponse, webhook, path=["response"])

    @parametrize
    async def test_raw_response_validate(self, async_client: AsyncAvido) -> None:
        response = await async_client.webhook.with_raw_response.validate(
            body={},
            signature="signature",
            timestamp=1687802842609,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook = await response.parse()
        assert_matches_type(WebhookValidateResponse, webhook, path=["response"])

    @parametrize
    async def test_streaming_response_validate(self, async_client: AsyncAvido) -> None:
        async with async_client.webhook.with_streaming_response.validate(
            body={},
            signature="signature",
            timestamp=1687802842609,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook = await response.parse()
            assert_matches_type(WebhookValidateResponse, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True
