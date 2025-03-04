# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["TestListParams"]


class TestListParams(TypedDict, total=False):
    application_slug: Annotated[str, PropertyInfo(alias="applicationSlug")]
    """Filter by application slug"""

    end_date: Annotated[Union[str, datetime], PropertyInfo(alias="endDate", format="iso8601")]
    """Filter tests created before this date"""

    evaluation_case_id: Annotated[str, PropertyInfo(alias="evaluationCaseId")]
    """Filter by evaluation case ID"""

    limit: int
    """Number of items per page"""

    order_by: Annotated[str, PropertyInfo(alias="orderBy")]
    """Field to order by"""

    order_dir: Annotated[Literal["asc", "desc"], PropertyInfo(alias="orderDir")]
    """Order direction"""

    skip: int
    """Number of items to skip"""

    start_date: Annotated[Union[str, datetime], PropertyInfo(alias="startDate", format="iso8601")]
    """Filter tests created after this date"""

    statuses: str
    """Comma-separated list of test statuses to filter by.

    Defaults to "COMPLETED" if not supplied.
    """
