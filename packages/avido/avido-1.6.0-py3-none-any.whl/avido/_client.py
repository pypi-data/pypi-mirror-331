# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Dict, Union, Mapping, cast
from typing_extensions import Self, Literal, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    NOT_GIVEN,
    Omit,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
)
from ._utils import (
    is_given,
    get_async_library,
)
from ._version import __version__
from .resources import tests, ingests, threads, webhook, evaluations, applications, evaluation_topics
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import AvidoError, APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)

__all__ = [
    "ENVIRONMENTS",
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "Avido",
    "AsyncAvido",
    "Client",
    "AsyncClient",
]

ENVIRONMENTS: Dict[str, str] = {
    "production": "https://api.avidoai.com",
    "sandbox": "https://sandbox.avidoai.com",
}


class Avido(SyncAPIClient):
    webhook: webhook.WebhookResource
    evaluations: evaluations.EvaluationsResource
    applications: applications.ApplicationsResource
    evaluation_topics: evaluation_topics.EvaluationTopicsResource
    tests: tests.TestsResource
    ingests: ingests.IngestsResource
    threads: threads.ThreadsResource
    with_raw_response: AvidoWithRawResponse
    with_streaming_response: AvidoWithStreamedResponse

    # client options
    api_key: str
    application_id: str

    _environment: Literal["production", "sandbox"] | NotGiven

    def __init__(
        self,
        *,
        api_key: str | None = None,
        application_id: str | None = None,
        environment: Literal["production", "sandbox"] | NotGiven = NOT_GIVEN,
        base_url: str | httpx.URL | None | NotGiven = NOT_GIVEN,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous Avido client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `api_key` from `AVIDO_API_KEY`
        - `application_id` from `AVIDO_APPLICATION_ID`
        """
        if api_key is None:
            api_key = os.environ.get("AVIDO_API_KEY")
        if api_key is None:
            raise AvidoError(
                "The api_key client option must be set either by passing api_key to the client or by setting the AVIDO_API_KEY environment variable"
            )
        self.api_key = api_key

        if application_id is None:
            application_id = os.environ.get("AVIDO_APPLICATION_ID")
        if application_id is None:
            raise AvidoError(
                "The application_id client option must be set either by passing application_id to the client or by setting the AVIDO_APPLICATION_ID environment variable"
            )
        self.application_id = application_id

        self._environment = environment

        base_url_env = os.environ.get("AVIDO_BASE_URL")
        if is_given(base_url) and base_url is not None:
            # cast required because mypy doesn't understand the type narrowing
            base_url = cast("str | httpx.URL", base_url)  # pyright: ignore[reportUnnecessaryCast]
        elif is_given(environment):
            if base_url_env and base_url is not None:
                raise ValueError(
                    "Ambiguous URL; The `AVIDO_BASE_URL` env var and the `environment` argument are given. If you want to use the environment, you must pass base_url=None",
                )

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc
        elif base_url_env is not None:
            base_url = base_url_env
        else:
            self._environment = environment = "production"

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.webhook = webhook.WebhookResource(self)
        self.evaluations = evaluations.EvaluationsResource(self)
        self.applications = applications.ApplicationsResource(self)
        self.evaluation_topics = evaluation_topics.EvaluationTopicsResource(self)
        self.tests = tests.TestsResource(self)
        self.ingests = ingests.IngestsResource(self)
        self.threads = threads.ThreadsResource(self)
        self.with_raw_response = AvidoWithRawResponse(self)
        self.with_streaming_response = AvidoWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        if self._api_key:
            return self._api_key
        if self._application_id:
            return self._application_id
        return {}

    @property
    def _api_key(self) -> dict[str, str]:
        api_key = self.api_key
        return {"x-api-key": api_key}

    @property
    def _application_id(self) -> dict[str, str]:
        application_id = self.application_id
        return {"x-application-id": application_id}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        application_id: str | None = None,
        environment: Literal["production", "sandbox"] | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            application_id=application_id or self.application_id,
            base_url=base_url or self.base_url,
            environment=environment or self._environment,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncAvido(AsyncAPIClient):
    webhook: webhook.AsyncWebhookResource
    evaluations: evaluations.AsyncEvaluationsResource
    applications: applications.AsyncApplicationsResource
    evaluation_topics: evaluation_topics.AsyncEvaluationTopicsResource
    tests: tests.AsyncTestsResource
    ingests: ingests.AsyncIngestsResource
    threads: threads.AsyncThreadsResource
    with_raw_response: AsyncAvidoWithRawResponse
    with_streaming_response: AsyncAvidoWithStreamedResponse

    # client options
    api_key: str
    application_id: str

    _environment: Literal["production", "sandbox"] | NotGiven

    def __init__(
        self,
        *,
        api_key: str | None = None,
        application_id: str | None = None,
        environment: Literal["production", "sandbox"] | NotGiven = NOT_GIVEN,
        base_url: str | httpx.URL | None | NotGiven = NOT_GIVEN,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncAvido client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `api_key` from `AVIDO_API_KEY`
        - `application_id` from `AVIDO_APPLICATION_ID`
        """
        if api_key is None:
            api_key = os.environ.get("AVIDO_API_KEY")
        if api_key is None:
            raise AvidoError(
                "The api_key client option must be set either by passing api_key to the client or by setting the AVIDO_API_KEY environment variable"
            )
        self.api_key = api_key

        if application_id is None:
            application_id = os.environ.get("AVIDO_APPLICATION_ID")
        if application_id is None:
            raise AvidoError(
                "The application_id client option must be set either by passing application_id to the client or by setting the AVIDO_APPLICATION_ID environment variable"
            )
        self.application_id = application_id

        self._environment = environment

        base_url_env = os.environ.get("AVIDO_BASE_URL")
        if is_given(base_url) and base_url is not None:
            # cast required because mypy doesn't understand the type narrowing
            base_url = cast("str | httpx.URL", base_url)  # pyright: ignore[reportUnnecessaryCast]
        elif is_given(environment):
            if base_url_env and base_url is not None:
                raise ValueError(
                    "Ambiguous URL; The `AVIDO_BASE_URL` env var and the `environment` argument are given. If you want to use the environment, you must pass base_url=None",
                )

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc
        elif base_url_env is not None:
            base_url = base_url_env
        else:
            self._environment = environment = "production"

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.webhook = webhook.AsyncWebhookResource(self)
        self.evaluations = evaluations.AsyncEvaluationsResource(self)
        self.applications = applications.AsyncApplicationsResource(self)
        self.evaluation_topics = evaluation_topics.AsyncEvaluationTopicsResource(self)
        self.tests = tests.AsyncTestsResource(self)
        self.ingests = ingests.AsyncIngestsResource(self)
        self.threads = threads.AsyncThreadsResource(self)
        self.with_raw_response = AsyncAvidoWithRawResponse(self)
        self.with_streaming_response = AsyncAvidoWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        if self._api_key:
            return self._api_key
        if self._application_id:
            return self._application_id
        return {}

    @property
    def _api_key(self) -> dict[str, str]:
        api_key = self.api_key
        return {"x-api-key": api_key}

    @property
    def _application_id(self) -> dict[str, str]:
        application_id = self.application_id
        return {"x-application-id": application_id}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        application_id: str | None = None,
        environment: Literal["production", "sandbox"] | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            application_id=application_id or self.application_id,
            base_url=base_url or self.base_url,
            environment=environment or self._environment,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AvidoWithRawResponse:
    def __init__(self, client: Avido) -> None:
        self.webhook = webhook.WebhookResourceWithRawResponse(client.webhook)
        self.evaluations = evaluations.EvaluationsResourceWithRawResponse(client.evaluations)
        self.applications = applications.ApplicationsResourceWithRawResponse(client.applications)
        self.evaluation_topics = evaluation_topics.EvaluationTopicsResourceWithRawResponse(client.evaluation_topics)
        self.tests = tests.TestsResourceWithRawResponse(client.tests)
        self.ingests = ingests.IngestsResourceWithRawResponse(client.ingests)
        self.threads = threads.ThreadsResourceWithRawResponse(client.threads)


class AsyncAvidoWithRawResponse:
    def __init__(self, client: AsyncAvido) -> None:
        self.webhook = webhook.AsyncWebhookResourceWithRawResponse(client.webhook)
        self.evaluations = evaluations.AsyncEvaluationsResourceWithRawResponse(client.evaluations)
        self.applications = applications.AsyncApplicationsResourceWithRawResponse(client.applications)
        self.evaluation_topics = evaluation_topics.AsyncEvaluationTopicsResourceWithRawResponse(
            client.evaluation_topics
        )
        self.tests = tests.AsyncTestsResourceWithRawResponse(client.tests)
        self.ingests = ingests.AsyncIngestsResourceWithRawResponse(client.ingests)
        self.threads = threads.AsyncThreadsResourceWithRawResponse(client.threads)


class AvidoWithStreamedResponse:
    def __init__(self, client: Avido) -> None:
        self.webhook = webhook.WebhookResourceWithStreamingResponse(client.webhook)
        self.evaluations = evaluations.EvaluationsResourceWithStreamingResponse(client.evaluations)
        self.applications = applications.ApplicationsResourceWithStreamingResponse(client.applications)
        self.evaluation_topics = evaluation_topics.EvaluationTopicsResourceWithStreamingResponse(
            client.evaluation_topics
        )
        self.tests = tests.TestsResourceWithStreamingResponse(client.tests)
        self.ingests = ingests.IngestsResourceWithStreamingResponse(client.ingests)
        self.threads = threads.ThreadsResourceWithStreamingResponse(client.threads)


class AsyncAvidoWithStreamedResponse:
    def __init__(self, client: AsyncAvido) -> None:
        self.webhook = webhook.AsyncWebhookResourceWithStreamingResponse(client.webhook)
        self.evaluations = evaluations.AsyncEvaluationsResourceWithStreamingResponse(client.evaluations)
        self.applications = applications.AsyncApplicationsResourceWithStreamingResponse(client.applications)
        self.evaluation_topics = evaluation_topics.AsyncEvaluationTopicsResourceWithStreamingResponse(
            client.evaluation_topics
        )
        self.tests = tests.AsyncTestsResourceWithStreamingResponse(client.tests)
        self.ingests = ingests.AsyncIngestsResourceWithStreamingResponse(client.ingests)
        self.threads = threads.AsyncThreadsResourceWithStreamingResponse(client.threads)


Client = Avido

AsyncClient = AsyncAvido
