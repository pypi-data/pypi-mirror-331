from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1Toleration(BaseModel):
    effect : Optional[str] = Field(default = None, alias = "effect")
    key : Optional[str] = Field(default = None, alias = "key")
    operator : Optional[str] = Field(default = None, alias = "operator")
    toleration_seconds : Optional[int] = Field(default = None, alias = "tolerationSeconds")
    value : Optional[str] = Field(default = None, alias = "value")
