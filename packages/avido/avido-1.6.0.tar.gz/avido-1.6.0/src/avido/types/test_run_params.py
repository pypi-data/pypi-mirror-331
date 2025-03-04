# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["TestRunParams"]


class TestRunParams(TypedDict, total=False):
    evaluation_case_id: Required[Annotated[str, PropertyInfo(alias="evaluationCaseId")]]
    """ID of the evaluation case to run the test for"""
