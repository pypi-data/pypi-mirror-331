# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = [
    "IngestCreateParams",
    "Event",
    "EventThreadInput",
    "EventLlmTraceInput",
    "EventToolTraceInput",
    "EventRetrieverTraceInput",
    "EventLogTraceInput",
]


class IngestCreateParams(TypedDict, total=False):
    events: Required[Iterable[Event]]
    """Array of events to be ingested, which can be threads or traces."""


class EventThreadInput(TypedDict, total=False):
    timestamp: Required[str]
    """ISO-8601 datetime when the thread was triggered/created."""

    type: Required[Literal["thread"]]
    """Type of the event (always `thread` for threads)."""

    input: Union[str, Dict[str, object], Iterable[object], None]
    """JSON describing the input.

    Strings will be automatically parsed as JSON or wrapped in a message object.
    """

    metadata: Optional[Dict[str, object]]
    """Arbitrary metadata for this thread (e.g., userId, source, etc.)."""

    test_id: Optional[str]
    """Optional test/evaluation ID for the thread."""

    thread_id: str
    """Unique Thread ID (UUID). If not provided, it will be generated server-side."""


class EventLlmTraceInput(TypedDict, total=False):
    model_id: Required[str]
    """Model ID or name used for the LLM call."""

    thread_id: Required[str]
    """UUID referencing the parent thread's ID."""

    timestamp: Required[str]
    """ISO-8601 datetime for when the trace event occurred."""

    type: Required[Literal["llm"]]

    completion_tokens: Optional[float]
    """Number of completion tokens used by the LLM."""

    event: Optional[str]
    """Event label (e.g., 'start', 'end'). Specific to LLM traces."""

    input: Union[Dict[str, object], Iterable[object], None]
    """JSON input for this LLM trace event (e.g., the prompt)."""

    metadata: Optional[Dict[str, object]]
    """Extra metadata about this trace event."""

    output: Union[Dict[str, object], Iterable[object], None]
    """JSON output for this LLM trace event (e.g., the completion)."""

    params: Union[Dict[str, object], Iterable[object], None]
    """Arbitrary LLM params (temperature, top_p, etc.)."""

    prompt_tokens: Optional[float]
    """Number of prompt tokens used by the LLM."""


class EventToolTraceInput(TypedDict, total=False):
    thread_id: Required[str]
    """UUID referencing the parent thread's ID."""

    timestamp: Required[str]
    """ISO-8601 datetime for when the trace event occurred."""

    type: Required[Literal["tool"]]

    metadata: Optional[Dict[str, object]]
    """Extra metadata about this trace event."""

    tool_input: Union[Dict[str, object], Iterable[object], None]
    """JSON input for the tool call."""

    tool_output: Union[Dict[str, object], Iterable[object], None]
    """JSON output from the tool call."""


class EventRetrieverTraceInput(TypedDict, total=False):
    thread_id: Required[str]
    """UUID referencing the parent thread's ID."""

    timestamp: Required[str]
    """ISO-8601 datetime for when the trace event occurred."""

    type: Required[Literal["retriever"]]

    metadata: Optional[Dict[str, object]]
    """Extra metadata about this trace event."""

    retriever_query: Union[str, Dict[str, object], Iterable[object], None]
    """Query used for retrieval-augmented generation."""

    retriever_result: Union[Dict[str, object], Iterable[object], None]
    """Retrieved data chunks, if any."""


class EventLogTraceInput(TypedDict, total=False):
    thread_id: Required[str]
    """UUID referencing the parent thread's ID."""

    timestamp: Required[str]
    """ISO-8601 datetime for when the trace event occurred."""

    type: Required[Literal["log"]]

    content: Optional[str]
    """The actual log message for this trace."""

    metadata: Optional[Dict[str, object]]
    """Extra metadata about this trace event."""


Event: TypeAlias = Union[
    EventThreadInput, EventLlmTraceInput, EventToolTraceInput, EventRetrieverTraceInput, EventLogTraceInput
]
