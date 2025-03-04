# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from avido import Avido, AsyncAvido
from avido.types import (
    EvaluationListResponse,
    EvaluationCreateResponse,
    EvaluationRetrieveResponse,
)
from tests.utils import assert_matches_type
from avido.pagination import SyncOffsetPagination, AsyncOffsetPagination

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEvaluations:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Avido) -> None:
        evaluation = client.evaluations.create(
            application_id="456e4567-e89b-12d3-a456-426614174000",
            evaluation_criteria="The function should handle empty arrays, null values, and correctly sum all prices",
            factual_correctness=True,
            style_requirements=True,
            task="Implement a function to calculate the total price of items in a shopping cart",
            topic_id="789e4567-e89b-12d3-a456-426614174000",
        )
        assert_matches_type(EvaluationCreateResponse, evaluation, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Avido) -> None:
        response = client.evaluations.with_raw_response.create(
            application_id="456e4567-e89b-12d3-a456-426614174000",
            evaluation_criteria="The function should handle empty arrays, null values, and correctly sum all prices",
            factual_correctness=True,
            style_requirements=True,
            task="Implement a function to calculate the total price of items in a shopping cart",
            topic_id="789e4567-e89b-12d3-a456-426614174000",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = response.parse()
        assert_matches_type(EvaluationCreateResponse, evaluation, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Avido) -> None:
        with client.evaluations.with_streaming_response.create(
            application_id="456e4567-e89b-12d3-a456-426614174000",
            evaluation_criteria="The function should handle empty arrays, null values, and correctly sum all prices",
            factual_correctness=True,
            style_requirements=True,
            task="Implement a function to calculate the total price of items in a shopping cart",
            topic_id="789e4567-e89b-12d3-a456-426614174000",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = response.parse()
            assert_matches_type(EvaluationCreateResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: Avido) -> None:
        evaluation = client.evaluations.retrieve(
            "123e4567-e89b-12d3-a456-426614174000",
        )
        assert_matches_type(EvaluationRetrieveResponse, evaluation, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Avido) -> None:
        response = client.evaluations.with_raw_response.retrieve(
            "123e4567-e89b-12d3-a456-426614174000",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = response.parse()
        assert_matches_type(EvaluationRetrieveResponse, evaluation, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Avido) -> None:
        with client.evaluations.with_streaming_response.retrieve(
            "123e4567-e89b-12d3-a456-426614174000",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = response.parse()
            assert_matches_type(EvaluationRetrieveResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Avido) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.evaluations.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_list(self, client: Avido) -> None:
        evaluation = client.evaluations.list()
        assert_matches_type(SyncOffsetPagination[EvaluationListResponse], evaluation, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Avido) -> None:
        evaluation = client.evaluations.list(
            application_id="456e4567-e89b-12d3-a456-426614174000",
            application_slug="customer-support-bot",
            limit=25,
            order_by="createdAt",
            order_dir="asc",
            skip=0,
            topic_id="789e4567-e89b-12d3-a456-426614174000",
        )
        assert_matches_type(SyncOffsetPagination[EvaluationListResponse], evaluation, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Avido) -> None:
        response = client.evaluations.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = response.parse()
        assert_matches_type(SyncOffsetPagination[EvaluationListResponse], evaluation, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Avido) -> None:
        with client.evaluations.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = response.parse()
            assert_matches_type(SyncOffsetPagination[EvaluationListResponse], evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncEvaluations:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncAvido) -> None:
        evaluation = await async_client.evaluations.create(
            application_id="456e4567-e89b-12d3-a456-426614174000",
            evaluation_criteria="The function should handle empty arrays, null values, and correctly sum all prices",
            factual_correctness=True,
            style_requirements=True,
            task="Implement a function to calculate the total price of items in a shopping cart",
            topic_id="789e4567-e89b-12d3-a456-426614174000",
        )
        assert_matches_type(EvaluationCreateResponse, evaluation, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncAvido) -> None:
        response = await async_client.evaluations.with_raw_response.create(
            application_id="456e4567-e89b-12d3-a456-426614174000",
            evaluation_criteria="The function should handle empty arrays, null values, and correctly sum all prices",
            factual_correctness=True,
            style_requirements=True,
            task="Implement a function to calculate the total price of items in a shopping cart",
            topic_id="789e4567-e89b-12d3-a456-426614174000",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = await response.parse()
        assert_matches_type(EvaluationCreateResponse, evaluation, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncAvido) -> None:
        async with async_client.evaluations.with_streaming_response.create(
            application_id="456e4567-e89b-12d3-a456-426614174000",
            evaluation_criteria="The function should handle empty arrays, null values, and correctly sum all prices",
            factual_correctness=True,
            style_requirements=True,
            task="Implement a function to calculate the total price of items in a shopping cart",
            topic_id="789e4567-e89b-12d3-a456-426614174000",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = await response.parse()
            assert_matches_type(EvaluationCreateResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncAvido) -> None:
        evaluation = await async_client.evaluations.retrieve(
            "123e4567-e89b-12d3-a456-426614174000",
        )
        assert_matches_type(EvaluationRetrieveResponse, evaluation, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncAvido) -> None:
        response = await async_client.evaluations.with_raw_response.retrieve(
            "123e4567-e89b-12d3-a456-426614174000",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = await response.parse()
        assert_matches_type(EvaluationRetrieveResponse, evaluation, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncAvido) -> None:
        async with async_client.evaluations.with_streaming_response.retrieve(
            "123e4567-e89b-12d3-a456-426614174000",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = await response.parse()
            assert_matches_type(EvaluationRetrieveResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncAvido) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.evaluations.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncAvido) -> None:
        evaluation = await async_client.evaluations.list()
        assert_matches_type(AsyncOffsetPagination[EvaluationListResponse], evaluation, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncAvido) -> None:
        evaluation = await async_client.evaluations.list(
            application_id="456e4567-e89b-12d3-a456-426614174000",
            application_slug="customer-support-bot",
            limit=25,
            order_by="createdAt",
            order_dir="asc",
            skip=0,
            topic_id="789e4567-e89b-12d3-a456-426614174000",
        )
        assert_matches_type(AsyncOffsetPagination[EvaluationListResponse], evaluation, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncAvido) -> None:
        response = await async_client.evaluations.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = await response.parse()
        assert_matches_type(AsyncOffsetPagination[EvaluationListResponse], evaluation, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncAvido) -> None:
        async with async_client.evaluations.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = await response.parse()
            assert_matches_type(AsyncOffsetPagination[EvaluationListResponse], evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True
