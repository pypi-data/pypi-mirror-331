# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional

from .._models import BaseModel

__all__ = ["ListEventsResponse"]


class ListEventsResponse(BaseModel):
    id: str

    customer_id: Optional[str] = None

    data: Union[str, float, bool, Dict[str, object], List[object], None] = None

    name: str

    org_id: Optional[str] = None

    timestamp: str

    user: Union[str, float, bool, Dict[str, object], List[object], None] = None

    user_id: Optional[str] = None

    v: Optional[str] = None
