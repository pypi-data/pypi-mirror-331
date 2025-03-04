# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

import httpx

from ..types import ingest_create_params
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
from ..types.ingest_create_response import IngestCreateResponse

__all__ = ["IngestsResource", "AsyncIngestsResource"]


class IngestsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> IngestsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Avido-AI/avido-py#accessing-raw-response-data-eg-headers
        """
        return IngestsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> IngestsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Avido-AI/avido-py#with_streaming_response
        """
        return IngestsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        events: Iterable[ingest_create_params.Event],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> IngestCreateResponse:
        """
        Ingest an array of events (threads or traces) to store and process.

        Args:
          events: Array of events to be ingested, which can be threads or traces.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v0/ingest",
            body=maybe_transform({"events": events}, ingest_create_params.IngestCreateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IngestCreateResponse,
        )


class AsyncIngestsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncIngestsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Avido-AI/avido-py#accessing-raw-response-data-eg-headers
        """
        return AsyncIngestsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncIngestsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Avido-AI/avido-py#with_streaming_response
        """
        return AsyncIngestsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        events: Iterable[ingest_create_params.Event],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> IngestCreateResponse:
        """
        Ingest an array of events (threads or traces) to store and process.

        Args:
          events: Array of events to be ingested, which can be threads or traces.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v0/ingest",
            body=await async_maybe_transform({"events": events}, ingest_create_params.IngestCreateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IngestCreateResponse,
        )


class IngestsResourceWithRawResponse:
    def __init__(self, ingests: IngestsResource) -> None:
        self._ingests = ingests

        self.create = to_raw_response_wrapper(
            ingests.create,
        )


class AsyncIngestsResourceWithRawResponse:
    def __init__(self, ingests: AsyncIngestsResource) -> None:
        self._ingests = ingests

        self.create = async_to_raw_response_wrapper(
            ingests.create,
        )


class IngestsResourceWithStreamingResponse:
    def __init__(self, ingests: IngestsResource) -> None:
        self._ingests = ingests

        self.create = to_streamed_response_wrapper(
            ingests.create,
        )


class AsyncIngestsResourceWithStreamingResponse:
    def __init__(self, ingests: AsyncIngestsResource) -> None:
        self._ingests = ingests

        self.create = async_to_streamed_response_wrapper(
            ingests.create,
        )
