# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["EvaluationRetrieveResponse", "Data", "DataApplication", "DataTopic"]


class DataApplication(BaseModel):
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


class DataTopic(BaseModel):
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


class Data(BaseModel):
    id: str
    """Unique identifier of the evaluation case"""

    application: DataApplication
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

    topic: DataTopic
    """Details about an evaluation topic"""

    topic_id: str = FieldInfo(alias="topicId")
    """ID of the evaluation topic"""


class EvaluationRetrieveResponse(BaseModel):
    data: Data
    """Evaluation case configuration and metadata"""
