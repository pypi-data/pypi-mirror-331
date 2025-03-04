# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ThreadListParams"]


class ThreadListParams(TypedDict, total=False):
    org_id: Required[str]
    """Organization ID for filtering."""

    application_id: str
    """Application ID for filtering."""

    end: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """End date for filtering."""

    start: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Start date for filtering."""
