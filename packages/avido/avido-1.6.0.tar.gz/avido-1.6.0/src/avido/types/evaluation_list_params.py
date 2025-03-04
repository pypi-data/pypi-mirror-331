# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["EvaluationListParams"]


class EvaluationListParams(TypedDict, total=False):
    application_id: Annotated[str, PropertyInfo(alias="applicationId")]
    """Filter by application ID (cannot be used with applicationSlug)"""

    application_slug: Annotated[str, PropertyInfo(alias="applicationSlug")]
    """Filter by application slug (cannot be used with applicationId)"""

    limit: int
    """Number of items per page"""

    order_by: Annotated[str, PropertyInfo(alias="orderBy")]
    """Field to order by"""

    order_dir: Annotated[Literal["asc", "desc"], PropertyInfo(alias="orderDir")]
    """Order direction"""

    skip: int
    """Number of items to skip"""

    topic_id: Annotated[str, PropertyInfo(alias="topicId")]
    """Filter by topic ID"""
