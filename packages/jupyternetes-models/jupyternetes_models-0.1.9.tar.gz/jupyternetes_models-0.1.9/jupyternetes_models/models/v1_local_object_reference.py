from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1LocalObjectReference(BaseModel):
    name : Optional[str] = Field(default = None, alias = "name")
