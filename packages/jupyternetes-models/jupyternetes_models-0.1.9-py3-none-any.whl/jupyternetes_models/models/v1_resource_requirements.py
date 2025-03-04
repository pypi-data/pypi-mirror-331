from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_resource_claim import V1ResourceClaim


class V1ResourceRequirements(BaseModel):
    claims : Optional[list[V1ResourceClaim]] = Field(default = None, alias = "claims")
    limits : Optional[dict[str, str]] = Field(default = None, alias = "limits")
    requests : Optional[dict[str,str]] = Field(default = None, alias = "requests")