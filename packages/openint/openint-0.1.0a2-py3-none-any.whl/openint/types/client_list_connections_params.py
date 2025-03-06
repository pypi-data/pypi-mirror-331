# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, TypedDict

__all__ = ["ClientListConnectionsParams"]


class ClientListConnectionsParams(TypedDict, total=False):
    connector_config_id: str

    connector_name: Literal[
        "aircall",
        "airtable",
        "apollo",
        "beancount",
        "brex",
        "coda",
        "confluence",
        "debug",
        "discord",
        "finch",
        "firebase",
        "foreceipt",
        "fs",
        "github",
        "gong",
        "google",
        "greenhouse",
        "heron",
        "hubspot",
        "intercom",
        "jira",
        "kustomer",
        "lever",
        "linear",
        "lunchmoney",
        "merge",
        "microsoft",
        "mongodb",
        "moota",
        "onebrick",
        "outreach",
        "pipedrive",
        "plaid",
        "postgres",
        "qbo",
        "ramp",
        "revert",
        "salesforce",
        "salesloft",
        "saltedge",
        "slack",
        "splitwise",
        "spreadsheet",
        "stripe",
        "teller",
        "toggl",
        "twenty",
        "webhook",
        "wise",
        "xero",
        "yodlee",
        "zohodesk",
        "googledrive",
    ]
    """The name of the connector"""

    customer_id: str

    expand: List[Literal["connector"]]

    include_secrets: Literal["none", "basic", "all"]
    """Controls secret inclusion: none (default), basic (auth only), or all secrets"""

    limit: int

    offset: int
