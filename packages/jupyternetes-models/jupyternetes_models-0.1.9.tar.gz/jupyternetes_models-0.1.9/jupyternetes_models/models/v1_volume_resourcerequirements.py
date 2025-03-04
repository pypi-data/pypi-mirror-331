from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1VolumeResourceRequirements(BaseModel):
    limits : Optional[dict[str,str]] = Field(default = None, alias = "limits")
    requests : Optional[dict[str,str]] = Field(default = None, alias = "requests")