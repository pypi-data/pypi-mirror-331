from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1EmptyDirVolumeSource(BaseModel):
    medium : Optional[str] = Field(alias = "medium", default = None)
    size_limit : Optional[str] = Field(alias = "sizeLimit", default = None)