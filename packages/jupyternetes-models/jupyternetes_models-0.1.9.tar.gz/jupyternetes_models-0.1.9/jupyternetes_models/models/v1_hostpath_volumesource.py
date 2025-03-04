from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1HostPathVolumeSource(BaseModel):
    path : str = Field(alias = "path", default = None)
    type : Optional[str] = Field(alias = "type", default = None)
