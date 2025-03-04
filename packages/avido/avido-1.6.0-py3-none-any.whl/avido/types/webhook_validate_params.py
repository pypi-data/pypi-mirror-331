# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["WebhookValidateParams"]


class WebhookValidateParams(TypedDict, total=False):
    body: Required[object]
    """The actual payload being sent by the webhook"""

    signature: Required[str]
    """HMAC signature for the request body"""

    timestamp: Required[float]
    """Timestamp for the request in milliseconds"""
