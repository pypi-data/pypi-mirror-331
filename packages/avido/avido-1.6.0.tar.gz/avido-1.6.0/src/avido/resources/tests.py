# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Literal

import httpx

from ..types import test_run_params, test_list_params
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
from ..types.test_run_response import TestRunResponse
from ..types.test_list_response import TestListResponse
from ..types.test_retrieve_response import TestRetrieveResponse

__all__ = ["TestsResource", "AsyncTestsResource"]


class TestsResource(SyncAPIResource):
    __test__ = False

    @cached_property
    def with_raw_response(self) -> TestsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Avido-AI/avido-py#accessing-raw-response-data-eg-headers
        """
        return TestsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TestsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Avido-AI/avido-py#with_streaming_response
        """
        return TestsResourceWithStreamingResponse(self)

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
    ) -> TestRetrieveResponse:
        """
        Retrieves detailed information about a specific test including its associated
        evaluation case and runs.

        Args:
          id: The unique identifier of the test

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/v0/tests/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TestRetrieveResponse,
        )

    def list(
        self,
        *,
        application_slug: str | NotGiven = NOT_GIVEN,
        end_date: Union[str, datetime] | NotGiven = NOT_GIVEN,
        evaluation_case_id: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        order_by: str | NotGiven = NOT_GIVEN,
        order_dir: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        skip: int | NotGiven = NOT_GIVEN,
        start_date: Union[str, datetime] | NotGiven = NOT_GIVEN,
        statuses: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncOffsetPagination[TestListResponse]:
        """
        Retrieves a paginated list of tests with optional filtering.

        Args:
          application_slug: Filter by application slug

          end_date: Filter tests created before this date

          evaluation_case_id: Filter by evaluation case ID

          limit: Number of items per page

          order_by: Field to order by

          order_dir: Order direction

          skip: Number of items to skip

          start_date: Filter tests created after this date

          statuses: Comma-separated list of test statuses to filter by. Defaults to "COMPLETED" if
              not supplied.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/v0/tests",
            page=SyncOffsetPagination[TestListResponse],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "application_slug": application_slug,
                        "end_date": end_date,
                        "evaluation_case_id": evaluation_case_id,
                        "limit": limit,
                        "order_by": order_by,
                        "order_dir": order_dir,
                        "skip": skip,
                        "start_date": start_date,
                        "statuses": statuses,
                    },
                    test_list_params.TestListParams,
                ),
            ),
            model=TestListResponse,
        )

    def run(
        self,
        *,
        evaluation_case_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TestRunResponse:
        """
        Creates and triggers the execution of a test for an evaluation case.

        Args:
          evaluation_case_id: ID of the evaluation case to run the test for

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v0/tests/run",
            body=maybe_transform({"evaluation_case_id": evaluation_case_id}, test_run_params.TestRunParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TestRunResponse,
        )


class AsyncTestsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTestsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Avido-AI/avido-py#accessing-raw-response-data-eg-headers
        """
        return AsyncTestsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTestsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Avido-AI/avido-py#with_streaming_response
        """
        return AsyncTestsResourceWithStreamingResponse(self)

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
    ) -> TestRetrieveResponse:
        """
        Retrieves detailed information about a specific test including its associated
        evaluation case and runs.

        Args:
          id: The unique identifier of the test

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/v0/tests/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TestRetrieveResponse,
        )

    def list(
        self,
        *,
        application_slug: str | NotGiven = NOT_GIVEN,
        end_date: Union[str, datetime] | NotGiven = NOT_GIVEN,
        evaluation_case_id: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        order_by: str | NotGiven = NOT_GIVEN,
        order_dir: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        skip: int | NotGiven = NOT_GIVEN,
        start_date: Union[str, datetime] | NotGiven = NOT_GIVEN,
        statuses: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[TestListResponse, AsyncOffsetPagination[TestListResponse]]:
        """
        Retrieves a paginated list of tests with optional filtering.

        Args:
          application_slug: Filter by application slug

          end_date: Filter tests created before this date

          evaluation_case_id: Filter by evaluation case ID

          limit: Number of items per page

          order_by: Field to order by

          order_dir: Order direction

          skip: Number of items to skip

          start_date: Filter tests created after this date

          statuses: Comma-separated list of test statuses to filter by. Defaults to "COMPLETED" if
              not supplied.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/v0/tests",
            page=AsyncOffsetPagination[TestListResponse],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "application_slug": application_slug,
                        "end_date": end_date,
                        "evaluation_case_id": evaluation_case_id,
                        "limit": limit,
                        "order_by": order_by,
                        "order_dir": order_dir,
                        "skip": skip,
                        "start_date": start_date,
                        "statuses": statuses,
                    },
                    test_list_params.TestListParams,
                ),
            ),
            model=TestListResponse,
        )

    async def run(
        self,
        *,
        evaluation_case_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TestRunResponse:
        """
        Creates and triggers the execution of a test for an evaluation case.

        Args:
          evaluation_case_id: ID of the evaluation case to run the test for

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v0/tests/run",
            body=await async_maybe_transform({"evaluation_case_id": evaluation_case_id}, test_run_params.TestRunParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TestRunResponse,
        )


class TestsResourceWithRawResponse:
    __test__ = False

    def __init__(self, tests: TestsResource) -> None:
        self._tests = tests

        self.retrieve = to_raw_response_wrapper(
            tests.retrieve,
        )
        self.list = to_raw_response_wrapper(
            tests.list,
        )
        self.run = to_raw_response_wrapper(
            tests.run,
        )


class AsyncTestsResourceWithRawResponse:
    def __init__(self, tests: AsyncTestsResource) -> None:
        self._tests = tests

        self.retrieve = async_to_raw_response_wrapper(
            tests.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            tests.list,
        )
        self.run = async_to_raw_response_wrapper(
            tests.run,
        )


class TestsResourceWithStreamingResponse:
    __test__ = False

    def __init__(self, tests: TestsResource) -> None:
        self._tests = tests

        self.retrieve = to_streamed_response_wrapper(
            tests.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            tests.list,
        )
        self.run = to_streamed_response_wrapper(
            tests.run,
        )


class AsyncTestsResourceWithStreamingResponse:
    def __init__(self, tests: AsyncTestsResource) -> None:
        self._tests = tests

        self.retrieve = async_to_streamed_response_wrapper(
            tests.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            tests.list,
        )
        self.run = async_to_streamed_response_wrapper(
            tests.run,
        )
