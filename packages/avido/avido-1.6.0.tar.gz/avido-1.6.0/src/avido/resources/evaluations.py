# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import evaluation_list_params, evaluation_create_params
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
from ..pagination import SyncOffsetPagination, AsyncOffsetPagination
from .._base_client import AsyncPaginator, make_request_options
from ..types.evaluation_list_response import EvaluationListResponse
from ..types.evaluation_create_response import EvaluationCreateResponse
from ..types.evaluation_retrieve_response import EvaluationRetrieveResponse

__all__ = ["EvaluationsResource", "AsyncEvaluationsResource"]


class EvaluationsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> EvaluationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Avido-AI/avido-py#accessing-raw-response-data-eg-headers
        """
        return EvaluationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EvaluationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Avido-AI/avido-py#with_streaming_response
        """
        return EvaluationsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        application_id: str,
        evaluation_criteria: str,
        factual_correctness: bool,
        style_requirements: bool,
        task: str,
        topic_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EvaluationCreateResponse:
        """
        Creates a new evaluation case and triggers the chain of thought generation.

        Args:
          application_id: ID of the application this case belongs to

          evaluation_criteria: Criteria for evaluating the task

          factual_correctness: Whether factual correctness should be evaluated

          style_requirements: Whether style requirements should be evaluated

          task: The task to be evaluated

          topic_id: ID of the evaluation topic

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v0/evaluations",
            body=maybe_transform(
                {
                    "application_id": application_id,
                    "evaluation_criteria": evaluation_criteria,
                    "factual_correctness": factual_correctness,
                    "style_requirements": style_requirements,
                    "task": task,
                    "topic_id": topic_id,
                },
                evaluation_create_params.EvaluationCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvaluationCreateResponse,
        )

    def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EvaluationRetrieveResponse:
        """
        Retrieves detailed information about a specific evaluation case including its
        associated application and topic.

        Args:
          id: The unique identifier of the evaluation case

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/v0/evaluations/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvaluationRetrieveResponse,
        )

    def list(
        self,
        *,
        application_id: str | NotGiven = NOT_GIVEN,
        application_slug: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        order_by: str | NotGiven = NOT_GIVEN,
        order_dir: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        skip: int | NotGiven = NOT_GIVEN,
        topic_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncOffsetPagination[EvaluationListResponse]:
        """
        Retrieves a paginated list of evaluation cases with optional filtering.

        Args:
          application_id: Filter by application ID (cannot be used with applicationSlug)

          application_slug: Filter by application slug (cannot be used with applicationId)

          limit: Number of items per page

          order_by: Field to order by

          order_dir: Order direction

          skip: Number of items to skip

          topic_id: Filter by topic ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/v0/evaluations",
            page=SyncOffsetPagination[EvaluationListResponse],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "application_id": application_id,
                        "application_slug": application_slug,
                        "limit": limit,
                        "order_by": order_by,
                        "order_dir": order_dir,
                        "skip": skip,
                        "topic_id": topic_id,
                    },
                    evaluation_list_params.EvaluationListParams,
                ),
            ),
            model=EvaluationListResponse,
        )


class AsyncEvaluationsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncEvaluationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Avido-AI/avido-py#accessing-raw-response-data-eg-headers
        """
        return AsyncEvaluationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEvaluationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Avido-AI/avido-py#with_streaming_response
        """
        return AsyncEvaluationsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        application_id: str,
        evaluation_criteria: str,
        factual_correctness: bool,
        style_requirements: bool,
        task: str,
        topic_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EvaluationCreateResponse:
        """
        Creates a new evaluation case and triggers the chain of thought generation.

        Args:
          application_id: ID of the application this case belongs to

          evaluation_criteria: Criteria for evaluating the task

          factual_correctness: Whether factual correctness should be evaluated

          style_requirements: Whether style requirements should be evaluated

          task: The task to be evaluated

          topic_id: ID of the evaluation topic

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v0/evaluations",
            body=await async_maybe_transform(
                {
                    "application_id": application_id,
                    "evaluation_criteria": evaluation_criteria,
                    "factual_correctness": factual_correctness,
                    "style_requirements": style_requirements,
                    "task": task,
                    "topic_id": topic_id,
                },
                evaluation_create_params.EvaluationCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvaluationCreateResponse,
        )

    async def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EvaluationRetrieveResponse:
        """
        Retrieves detailed information about a specific evaluation case including its
        associated application and topic.

        Args:
          id: The unique identifier of the evaluation case

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/v0/evaluations/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvaluationRetrieveResponse,
        )

    def list(
        self,
        *,
        application_id: str | NotGiven = NOT_GIVEN,
        application_slug: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        order_by: str | NotGiven = NOT_GIVEN,
        order_dir: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        skip: int | NotGiven = NOT_GIVEN,
        topic_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[EvaluationListResponse, AsyncOffsetPagination[EvaluationListResponse]]:
        """
        Retrieves a paginated list of evaluation cases with optional filtering.

        Args:
          application_id: Filter by application ID (cannot be used with applicationSlug)

          application_slug: Filter by application slug (cannot be used with applicationId)

          limit: Number of items per page

          order_by: Field to order by

          order_dir: Order direction

          skip: Number of items to skip

          topic_id: Filter by topic ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/v0/evaluations",
            page=AsyncOffsetPagination[EvaluationListResponse],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "application_id": application_id,
                        "application_slug": application_slug,
                        "limit": limit,
                        "order_by": order_by,
                        "order_dir": order_dir,
                        "skip": skip,
                        "topic_id": topic_id,
                    },
                    evaluation_list_params.EvaluationListParams,
                ),
            ),
            model=EvaluationListResponse,
        )


class EvaluationsResourceWithRawResponse:
    def __init__(self, evaluations: EvaluationsResource) -> None:
        self._evaluations = evaluations

        self.create = to_raw_response_wrapper(
            evaluations.create,
        )
        self.retrieve = to_raw_response_wrapper(
            evaluations.retrieve,
        )
        self.list = to_raw_response_wrapper(
            evaluations.list,
        )


class AsyncEvaluationsResourceWithRawResponse:
    def __init__(self, evaluations: AsyncEvaluationsResource) -> None:
        self._evaluations = evaluations

        self.create = async_to_raw_response_wrapper(
            evaluations.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            evaluations.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            evaluations.list,
        )


class EvaluationsResourceWithStreamingResponse:
    def __init__(self, evaluations: EvaluationsResource) -> None:
        self._evaluations = evaluations

        self.create = to_streamed_response_wrapper(
            evaluations.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            evaluations.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            evaluations.list,
        )


class AsyncEvaluationsResourceWithStreamingResponse:
    def __init__(self, evaluations: AsyncEvaluationsResource) -> None:
        self._evaluations = evaluations

        self.create = async_to_streamed_response_wrapper(
            evaluations.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            evaluations.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            evaluations.list,
        )
