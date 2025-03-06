# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["ClientCreateMagicLinkParams"]


class ClientCreateMagicLinkParams(TypedDict, total=False):
    customer_id: Required[str]

    connection_id: Optional[str]

    connector_names: Optional[
        Literal[
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
    ]
    """Filter integrations by comma separated connector names"""

    email: str
    """The email address of the customer"""

    redirect_url: Optional[str]
    """Where to send user to after connect / if they press back button"""

    theme: Optional[Literal["light", "dark"]]
    """Magic Link display theme"""

    validity_in_seconds: float
    """How long the magic link will be valid for (in seconds) before it expires"""

    view: Optional[Literal["manage", "manage-deeplink", "add", "add-deeplink"]]
    """Magic Link tab view"""
