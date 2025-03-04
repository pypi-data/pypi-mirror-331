# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from typing_extensions import TypeAlias

from .._models import BaseModel

__all__ = ["ThreadListResponse", "ThreadListResponseItem"]


class ThreadListResponseItem(BaseModel):
    application_id: str
    """Application ID (UUID)."""

    org_id: str
    """Organization ID"""

    thread_id: str
    """Unique Thread ID (UUID)."""

    timestamp: str
    """ISO-8601 datetime when the thread was triggered/created."""

    input: Union[Dict[str, object], List[object], None] = None
    """JSON describing the initial input that started the thread.

    Strings will be automatically parsed as JSON or wrapped in a message object.
    """

    metadata: Optional[Dict[str, object]] = None
    """Arbitrary metadata for this thread (e.g., userId, source, etc.)."""

    test_id: Optional[str] = None
    """Optional test/evaluation ID for the thread."""


ThreadListResponse: TypeAlias = List[ThreadListResponseItem]
