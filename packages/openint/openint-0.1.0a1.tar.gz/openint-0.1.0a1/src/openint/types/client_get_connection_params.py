# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, TypedDict

__all__ = ["ClientGetConnectionParams"]


class ClientGetConnectionParams(TypedDict, total=False):
    connector_config_id: str

    connector_name: str

    customer_id: str

    expand: List[Literal["connector"]]

    include_secrets: Literal["none", "basic", "all"]
    """Controls secret inclusion: none (default), basic (auth only), or all secrets"""

    limit: int

    offset: int
