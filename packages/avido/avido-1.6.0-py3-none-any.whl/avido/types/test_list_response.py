# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["TestListResponse", "EvaluationCase", "EvaluationCaseApplication", "EvaluationCaseTopic"]


class EvaluationCaseApplication(BaseModel):
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


class EvaluationCaseTopic(BaseModel):
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


class EvaluationCase(BaseModel):
    id: str
    """Unique identifier of the evaluation case"""

    application: EvaluationCaseApplication
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

    topic: EvaluationCaseTopic
    """Details about an evaluation topic"""

    topic_id: str = FieldInfo(alias="topicId")
    """ID of the evaluation topic"""


class TestListResponse(BaseModel):
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

    evaluation_case: EvaluationCase = FieldInfo(alias="evaluationCase")
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
