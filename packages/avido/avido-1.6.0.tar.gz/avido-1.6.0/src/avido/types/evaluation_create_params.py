# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["EvaluationCreateParams"]


class EvaluationCreateParams(TypedDict, total=False):
    application_id: Required[Annotated[str, PropertyInfo(alias="applicationId")]]
    """ID of the application this case belongs to"""

    evaluation_criteria: Required[Annotated[str, PropertyInfo(alias="evaluationCriteria")]]
    """Criteria for evaluating the task"""

    factual_correctness: Required[Annotated[bool, PropertyInfo(alias="factualCorrectness")]]
    """Whether factual correctness should be evaluated"""

    style_requirements: Required[Annotated[bool, PropertyInfo(alias="styleRequirements")]]
    """Whether style requirements should be evaluated"""

    task: Required[str]
    """The task to be evaluated"""

    topic_id: Required[Annotated[str, PropertyInfo(alias="topicId")]]
    """ID of the evaluation topic"""
