from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_keytopath import V1KeyToPath

class V1ConfigMapProjection(BaseModel):
    items : Optional[list[V1KeyToPath]] = Field(alias = "items", default = None)
    name : Optional[str] = Field(alias = "name", default = None)
    optional : Optional[bool] = Field(alias = "optional", default = None)