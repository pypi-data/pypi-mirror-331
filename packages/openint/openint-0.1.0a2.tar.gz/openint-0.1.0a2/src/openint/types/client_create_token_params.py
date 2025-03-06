# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ClientCreateTokenParams"]


class ClientCreateTokenParams(TypedDict, total=False):
    customer_id: Required[str]
    """
    Anything that uniquely identifies the customer that you will be sending the
    token to
    """

    validity_in_seconds: float
    """How long the token will be valid for (in seconds) before it expires"""
