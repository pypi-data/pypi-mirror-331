from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1ServiceAccountTokenProjection(BaseModel):
    audience : Optional[str] = Field(default = None, alias = "audience")
    expiration_seconds : Optional[int] = Field(default = None, alias = "expirationSeconds")
    path : str = Field(default = None, alias = "path")