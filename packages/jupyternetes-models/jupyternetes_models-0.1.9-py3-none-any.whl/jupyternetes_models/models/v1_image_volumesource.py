from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1ImageVolumeSource(BaseModel):
    pull_policy : Optional[str] = Field(default = None, alias = "pullPolicy")
    reference : Optional[str] = Field(default = None, alias = "reference")