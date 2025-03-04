from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1ResourceClaim(BaseModel):
    name : str = Field(default = None, alias = "name")
    request : Optional[str] = Field(default = None, alias = "request")
