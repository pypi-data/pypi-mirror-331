from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1PodDNSConfigOption(BaseModel):
    name : Optional[str] = Field(default = None, alias = "name")
    value : Optional[str] = Field(default = None, alias = "value")