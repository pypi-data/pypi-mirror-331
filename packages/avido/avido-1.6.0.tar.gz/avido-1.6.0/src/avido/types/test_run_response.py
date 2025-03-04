# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = [
    "TestRunResponse",
    "Test",
    "TestEvaluationCase",
    "TestEvaluationCaseApplication",
    "TestEvaluationCaseTopic",
    "Trace",
    "TraceLlmTrace",
    "TraceToolTrace",
    "TraceRetrieverTrace",
    "TraceLogTrace",
]


class TestEvaluationCaseApplication(BaseModel):
    __test__ = False
    id: str
    """Unique identifier of the application"""

    context: str
    """Context/instructions for the application"""

    created_at: str = FieldInfo(alias="createdAt")
    """When the application was created"""

    description: str
    """Description of the application"""

    environment: Literal["DEV", "PROD"]
    """Environment of the application. Defaults to DEV."""

    modified_at: str = FieldInfo(alias="modifiedAt")
    """When the application was last modified"""

    monitoring_enabled: bool = FieldInfo(alias="monitoringEnabled")
    """Whether monitoring is enabled for the application"""

    org_id: str = FieldInfo(alias="orgId")
    """Organization ID that owns this application"""

    slug: str
    """URL-friendly slug for the application"""

    title: str
    """Title of the application"""

    type: Literal["CHATBOT", "AGENT"]
    """Type of the application"""


class TestEvaluationCaseTopic(BaseModel):
    __test__ = False
    id: str
    """Unique identifier of the evaluation topic"""

    baseline: Optional[float] = None
    """Optional baseline score for this topic"""

    created_at: str = FieldInfo(alias="createdAt")
    """When the topic was created"""

    modified_at: str = FieldInfo(alias="modifiedAt")
    """When the topic was last modified"""

    org_id: str = FieldInfo(alias="orgId")
    """Organization ID that owns this topic"""

    title: str
    """Title of the evaluation topic"""


class TestEvaluationCase(BaseModel):
    __test__ = False
    id: str
    """Unique identifier of the evaluation case"""

    application: TestEvaluationCaseApplication
    """Application configuration and metadata"""

    application_id: str = FieldInfo(alias="applicationId")
    """ID of the application this case belongs to"""

    baseline: Optional[float] = None
    """Optional baseline score for this case"""

    cot_approach: Optional[str] = FieldInfo(alias="cotApproach", default=None)
    """Chain of thought approach for evaluation"""

    created_at: str = FieldInfo(alias="createdAt")
    """When the case was created"""

    evaluation_criteria: str = FieldInfo(alias="evaluationCriteria")
    """Criteria for evaluating the task"""

    factual_correctness: bool = FieldInfo(alias="factualCorrectness")
    """Whether factual correctness should be evaluated"""

    modified_at: str = FieldInfo(alias="modifiedAt")
    """When the case was last modified"""

    org_id: str = FieldInfo(alias="orgId")
    """Organization ID that owns this case"""

    style_requirements: bool = FieldInfo(alias="styleRequirements")
    """Whether style requirements should be evaluated"""

    task: str
    """The task to be evaluated"""

    topic: TestEvaluationCaseTopic
    """Details about an evaluation topic"""

    topic_id: str = FieldInfo(alias="topicId")
    """ID of the evaluation topic"""


class Test(BaseModel):
    __test__ = False
    id: str
    """Unique identifier of the test"""

    analysis: Optional[str] = None
    """Analysis of the test results"""

    clarity_score: Optional[float] = FieldInfo(alias="clarityScore", default=None)
    """Clarity score of the response"""

    coherence_score: Optional[float] = FieldInfo(alias="coherenceScore", default=None)
    """Coherence score of the response"""

    created_at: str = FieldInfo(alias="createdAt")
    """When the test was created"""

    engagingness_score: Optional[float] = FieldInfo(alias="engagingnessScore", default=None)
    """Engagingness score of the response"""

    evaluation_case: TestEvaluationCase = FieldInfo(alias="evaluationCase")
    """Evaluation case configuration and metadata"""

    evaluation_case_id: str = FieldInfo(alias="evaluationCaseId")
    """ID of the evaluation case this test belongs to"""

    factual_consistency_score: Optional[float] = FieldInfo(alias="factualConsistencyScore", default=None)
    """Factual consistency score of the response"""

    llm_response: Optional[str] = FieldInfo(alias="llmResponse", default=None)
    """The LLM's response to the test prompt"""

    modified_at: str = FieldInfo(alias="modifiedAt")
    """When the test was last modified"""

    naturalness_score: Optional[float] = FieldInfo(alias="naturalnessScore", default=None)
    """Naturalness score of the response"""

    org_id: str = FieldInfo(alias="orgId")
    """Organization ID that owns this test"""

    overall_score: Optional[float] = FieldInfo(alias="overallScore", default=None)
    """Overall score of the test"""

    relevance_score: Optional[float] = FieldInfo(alias="relevanceScore", default=None)
    """Relevance score of the response"""

    style_requirement_score: Optional[float] = FieldInfo(alias="styleRequirementScore", default=None)
    """Style requirement score of the response"""

    user_prompt: str = FieldInfo(alias="userPrompt")
    """The user prompt for the test"""


class TraceLlmTrace(BaseModel):
    application_id: str
    """Application ID (UUID)."""

    api_model_id: str = FieldInfo(alias="model_id")
    """Model ID or name used for the LLM call."""

    org_id: str
    """Organization ID (UUID)."""

    thread_id: str
    """UUID referencing the parent thread's ID."""

    timestamp: str
    """ISO-8601 datetime for when the trace event occurred."""

    trace_id: str
    """UUID for the trace."""

    type: Literal["llm"]

    completion_tokens: Optional[float] = None
    """Number of completion tokens used by the LLM."""

    event: Optional[str] = None
    """Event label (e.g., 'start', 'end'). Specific to LLM traces."""

    input: Union[Dict[str, object], List[object], None] = None
    """JSON input for this LLM trace event (e.g., the prompt)."""

    metadata: Optional[Dict[str, object]] = None
    """Extra metadata about this trace event."""

    output: Union[Dict[str, object], List[object], None] = None
    """JSON describing the output.

    Strings will be automatically parsed as JSON or wrapped in a message object.
    """

    params: Union[Dict[str, object], List[object], None] = None
    """Arbitrary LLM params (temperature, top_p, etc.)."""

    prompt_tokens: Optional[float] = None
    """Number of prompt tokens used by the LLM."""


class TraceToolTrace(BaseModel):
    application_id: str
    """Application ID (UUID)."""

    org_id: str
    """Organization ID (UUID)."""

    thread_id: str
    """UUID referencing the parent thread's ID."""

    timestamp: str
    """ISO-8601 datetime for when the trace event occurred."""

    trace_id: str
    """UUID for the trace."""

    type: Literal["tool"]

    metadata: Optional[Dict[str, object]] = None
    """Extra metadata about this trace event."""

    tool_input: Union[Dict[str, object], List[object], None] = None
    """JSON input for the tool call."""

    tool_output: Union[Dict[str, object], List[object], None] = None
    """JSON output from the tool call."""


class TraceRetrieverTrace(BaseModel):
    application_id: str
    """Application ID (UUID)."""

    org_id: str
    """Organization ID (UUID)."""

    thread_id: str
    """UUID referencing the parent thread's ID."""

    timestamp: str
    """ISO-8601 datetime for when the trace event occurred."""

    trace_id: str
    """UUID for the trace."""

    type: Literal["retriever"]

    metadata: Optional[Dict[str, object]] = None
    """Extra metadata about this trace event."""

    retriever_query: Union[Dict[str, object], List[object], None] = None
    """Query used for RAG."""

    retriever_result: Union[Dict[str, object], List[object], None] = None
    """Retrieved data chunks, if any."""


class TraceLogTrace(BaseModel):
    application_id: str
    """Application ID (UUID)."""

    org_id: str
    """Organization ID (UUID)."""

    thread_id: str
    """UUID referencing the parent thread's ID."""

    timestamp: str
    """ISO-8601 datetime for when the trace event occurred."""

    trace_id: str
    """UUID for the trace."""

    type: Literal["log"]

    content: Optional[str] = None
    """The actual log message for this trace."""

    metadata: Optional[Dict[str, object]] = None
    """Extra metadata about this trace event."""


Trace: TypeAlias = Union[TraceLlmTrace, TraceToolTrace, TraceRetrieverTrace, TraceLogTrace]


class TestRunResponse(BaseModel):
    __test__ = False
    test: Test
    """Complete test with related evaluation case and runs information"""

    traces: List[Trace]
