from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1HostAlias(BaseModel):
    hostnames : Optional[list[str]] = Field(alias = "hostnames", default = None)
    ip : str = Field(alias = "ip", default = None)
