from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1PodResourceClaim(BaseModel):
    name : str = Field(default = None, alias = "name")
    resource_claim_name : Optional[str] = Field(default = None, alias = "resourceClaimName")
    resource_claim_template_name : Optional[str] = Field(default = None, alias = "resourceClaimTemplateName")
