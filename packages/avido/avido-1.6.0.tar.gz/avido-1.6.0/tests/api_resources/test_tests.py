# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from avido import Avido, AsyncAvido
from avido.types import TestRunResponse, TestListResponse, TestRetrieveResponse
from tests.utils import assert_matches_type
from avido._utils import parse_datetime
from avido.pagination import SyncOffsetPagination, AsyncOffsetPagination

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTests:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: Avido) -> None:
        test = client.tests.retrieve(
            "123e4567-e89b-12d3-a456-426614174000",
        )
        assert_matches_type(TestRetrieveResponse, test, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Avido) -> None:
        response = client.tests.with_raw_response.retrieve(
            "123e4567-e89b-12d3-a456-426614174000",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = response.parse()
        assert_matches_type(TestRetrieveResponse, test, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Avido) -> None:
        with client.tests.with_streaming_response.retrieve(
            "123e4567-e89b-12d3-a456-426614174000",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = response.parse()
            assert_matches_type(TestRetrieveResponse, test, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Avido) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.tests.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_list(self, client: Avido) -> None:
        test = client.tests.list()
        assert_matches_type(SyncOffsetPagination[TestListResponse], test, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Avido) -> None:
        test = client.tests.list(
            application_slug="customer-support-bot",
            end_date=parse_datetime("2024-01-31T23:59:59.999Z"),
            evaluation_case_id="456e4567-e89b-12d3-a456-426614174000",
            limit=25,
            order_by="createdAt",
            order_dir="asc",
            skip=0,
            start_date=parse_datetime("2024-01-01T00:00:00.000Z"),
            statuses="COMPLETED,FAILED",
        )
        assert_matches_type(SyncOffsetPagination[TestListResponse], test, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Avido) -> None:
        response = client.tests.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = response.parse()
        assert_matches_type(SyncOffsetPagination[TestListResponse], test, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Avido) -> None:
        with client.tests.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = response.parse()
            assert_matches_type(SyncOffsetPagination[TestListResponse], test, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_run(self, client: Avido) -> None:
        test = client.tests.run(
            evaluation_case_id="456e4567-e89b-12d3-a456-426614174000",
        )
        assert_matches_type(TestRunResponse, test, path=["response"])

    @parametrize
    def test_raw_response_run(self, client: Avido) -> None:
        response = client.tests.with_raw_response.run(
            evaluation_case_id="456e4567-e89b-12d3-a456-426614174000",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = response.parse()
        assert_matches_type(TestRunResponse, test, path=["response"])

    @parametrize
    def test_streaming_response_run(self, client: Avido) -> None:
        with client.tests.with_streaming_response.run(
            evaluation_case_id="456e4567-e89b-12d3-a456-426614174000",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = response.parse()
            assert_matches_type(TestRunResponse, test, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncTests:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncAvido) -> None:
        test = await async_client.tests.retrieve(
            "123e4567-e89b-12d3-a456-426614174000",
        )
        assert_matches_type(TestRetrieveResponse, test, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncAvido) -> None:
        response = await async_client.tests.with_raw_response.retrieve(
            "123e4567-e89b-12d3-a456-426614174000",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = await response.parse()
        assert_matches_type(TestRetrieveResponse, test, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncAvido) -> None:
        async with async_client.tests.with_streaming_response.retrieve(
            "123e4567-e89b-12d3-a456-426614174000",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = await response.parse()
            assert_matches_type(TestRetrieveResponse, test, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncAvido) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.tests.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncAvido) -> None:
        test = await async_client.tests.list()
        assert_matches_type(AsyncOffsetPagination[TestListResponse], test, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncAvido) -> None:
        test = await async_client.tests.list(
            application_slug="customer-support-bot",
            end_date=parse_datetime("2024-01-31T23:59:59.999Z"),
            evaluation_case_id="456e4567-e89b-12d3-a456-426614174000",
            limit=25,
            order_by="createdAt",
            order_dir="asc",
            skip=0,
            start_date=parse_datetime("2024-01-01T00:00:00.000Z"),
            statuses="COMPLETED,FAILED",
        )
        assert_matches_type(AsyncOffsetPagination[TestListResponse], test, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncAvido) -> None:
        response = await async_client.tests.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = await response.parse()
        assert_matches_type(AsyncOffsetPagination[TestListResponse], test, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncAvido) -> None:
        async with async_client.tests.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = await response.parse()
            assert_matches_type(AsyncOffsetPagination[TestListResponse], test, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_run(self, async_client: AsyncAvido) -> None:
        test = await async_client.tests.run(
            evaluation_case_id="456e4567-e89b-12d3-a456-426614174000",
        )
        assert_matches_type(TestRunResponse, test, path=["response"])

    @parametrize
    async def test_raw_response_run(self, async_client: AsyncAvido) -> None:
        response = await async_client.tests.with_raw_response.run(
            evaluation_case_id="456e4567-e89b-12d3-a456-426614174000",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        test = await response.parse()
        assert_matches_type(TestRunResponse, test, path=["response"])

    @parametrize
    async def test_streaming_response_run(self, async_client: AsyncAvido) -> None:
        async with async_client.tests.with_streaming_response.run(
            evaluation_case_id="456e4567-e89b-12d3-a456-426614174000",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            test = await response.parse()
            assert_matches_type(TestRunResponse, test, path=["response"])

        assert cast(Any, response.is_closed) is True
