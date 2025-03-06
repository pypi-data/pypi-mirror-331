from typing import Any, Dict
import uuid
from pydantic import BaseModel, Field


class Headers_PM(BaseModel):
    correlationid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    origin: str = "not_applicable"
    origintype: str = "not_applicable"
    caller: str = "not_applicable"
    ipaddress: str = "not_applicable"
    origintype: str = "not_applicable"
    instanceid: str = "not_applicable"
    organizationid: str
    sessionid: str = "not_applicable"
    userid: str = "not_applicable"
    usertype: str = "not_applicable"
    eventid: str = "not_applicable"
    authorization: str

    def model_dump(self, exclude_fields={}, **kwargs) -> Dict[str, Any]:
        return super().model_dump(**kwargs, exclude=exclude_fields)


class RequestContext_PM(BaseModel):
    request_trace_id: str
    url_path: str
    method: str
