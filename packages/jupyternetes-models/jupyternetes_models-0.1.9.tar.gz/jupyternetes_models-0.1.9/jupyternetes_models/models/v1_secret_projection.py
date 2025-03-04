from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_keytopath import V1KeyToPath


class V1SecretProjection(BaseModel):
    items : Optional[list[V1KeyToPath]] = Field(default = None, alias = "items")
    name : Optional[str] = Field(default = None, alias = "name")
    optional : Optional[bool] = Field(default = None, alias = "optional")