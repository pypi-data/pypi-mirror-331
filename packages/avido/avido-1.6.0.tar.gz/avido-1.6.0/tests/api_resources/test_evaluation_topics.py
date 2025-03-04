# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from avido import Avido, AsyncAvido
from avido.types import (
    EvaluationTopicListResponse,
    EvaluationTopicCreateResponse,
    EvaluationTopicRetrieveResponse,
)
from tests.utils import assert_matches_type
from avido.pagination import SyncOffsetPagination, AsyncOffsetPagination

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEvaluationTopics:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Avido) -> None:
        evaluation_topic = client.evaluation_topics.create(
            title="Code Quality",
        )
        assert_matches_type(EvaluationTopicCreateResponse, evaluation_topic, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Avido) -> None:
        evaluation_topic = client.evaluation_topics.create(
            title="Code Quality",
            baseline=0.85,
        )
        assert_matches_type(EvaluationTopicCreateResponse, evaluation_topic, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Avido) -> None:
        response = client.evaluation_topics.with_raw_response.create(
            title="Code Quality",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation_topic = response.parse()
        assert_matches_type(EvaluationTopicCreateResponse, evaluation_topic, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Avido) -> None:
        with client.evaluation_topics.with_streaming_response.create(
            title="Code Quality",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation_topic = response.parse()
            assert_matches_type(EvaluationTopicCreateResponse, evaluation_topic, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: Avido) -> None:
        evaluation_topic = client.evaluation_topics.retrieve(
            "789e4567-e89b-12d3-a456-426614174000",
        )
        assert_matches_type(EvaluationTopicRetrieveResponse, evaluation_topic, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Avido) -> None:
        response = client.evaluation_topics.with_raw_response.retrieve(
            "789e4567-e89b-12d3-a456-426614174000",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation_topic = response.parse()
        assert_matches_type(EvaluationTopicRetrieveResponse, evaluation_topic, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Avido) -> None:
        with client.evaluation_topics.with_streaming_response.retrieve(
            "789e4567-e89b-12d3-a456-426614174000",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation_topic = response.parse()
            assert_matches_type(EvaluationTopicRetrieveResponse, evaluation_topic, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Avido) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.evaluation_topics.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_list(self, client: Avido) -> None:
        evaluation_topic = client.evaluation_topics.list()
        assert_matches_type(SyncOffsetPagination[EvaluationTopicListResponse], evaluation_topic, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Avido) -> None:
        evaluation_topic = client.evaluation_topics.list(
            limit=25,
            order_by="createdAt",
            order_dir="asc",
            skip=0,
            title="code quality",
        )
        assert_matches_type(SyncOffsetPagination[EvaluationTopicListResponse], evaluation_topic, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Avido) -> None:
        response = client.evaluation_topics.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation_topic = response.parse()
        assert_matches_type(SyncOffsetPagination[EvaluationTopicListResponse], evaluation_topic, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Avido) -> None:
        with client.evaluation_topics.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation_topic = response.parse()
            assert_matches_type(SyncOffsetPagination[EvaluationTopicListResponse], evaluation_topic, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncEvaluationTopics:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncAvido) -> None:
        evaluation_topic = await async_client.evaluation_topics.create(
            title="Code Quality",
        )
        assert_matches_type(EvaluationTopicCreateResponse, evaluation_topic, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncAvido) -> None:
        evaluation_topic = await async_client.evaluation_topics.create(
            title="Code Quality",
            baseline=0.85,
        )
        assert_matches_type(EvaluationTopicCreateResponse, evaluation_topic, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncAvido) -> None:
        response = await async_client.evaluation_topics.with_raw_response.create(
            title="Code Quality",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation_topic = await response.parse()
        assert_matches_type(EvaluationTopicCreateResponse, evaluation_topic, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncAvido) -> None:
        async with async_client.evaluation_topics.with_streaming_response.create(
            title="Code Quality",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation_topic = await response.parse()
            assert_matches_type(EvaluationTopicCreateResponse, evaluation_topic, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncAvido) -> None:
        evaluation_topic = await async_client.evaluation_topics.retrieve(
            "789e4567-e89b-12d3-a456-426614174000",
        )
        assert_matches_type(EvaluationTopicRetrieveResponse, evaluation_topic, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncAvido) -> None:
        response = await async_client.evaluation_topics.with_raw_response.retrieve(
            "789e4567-e89b-12d3-a456-426614174000",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation_topic = await response.parse()
        assert_matches_type(EvaluationTopicRetrieveResponse, evaluation_topic, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncAvido) -> None:
        async with async_client.evaluation_topics.with_streaming_response.retrieve(
            "789e4567-e89b-12d3-a456-426614174000",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation_topic = await response.parse()
            assert_matches_type(EvaluationTopicRetrieveResponse, evaluation_topic, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncAvido) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.evaluation_topics.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncAvido) -> None:
        evaluation_topic = await async_client.evaluation_topics.list()
        assert_matches_type(AsyncOffsetPagination[EvaluationTopicListResponse], evaluation_topic, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncAvido) -> None:
        evaluation_topic = await async_client.evaluation_topics.list(
            limit=25,
            order_by="createdAt",
            order_dir="asc",
            skip=0,
            title="code quality",
        )
        assert_matches_type(AsyncOffsetPagination[EvaluationTopicListResponse], evaluation_topic, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncAvido) -> None:
        response = await async_client.evaluation_topics.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation_topic = await response.parse()
        assert_matches_type(AsyncOffsetPagination[EvaluationTopicListResponse], evaluation_topic, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncAvido) -> None:
        async with async_client.evaluation_topics.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation_topic = await response.parse()
            assert_matches_type(AsyncOffsetPagination[EvaluationTopicListResponse], evaluation_topic, path=["response"])

        assert cast(Any, response.is_closed) is True
