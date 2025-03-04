from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1GlusterfsVolumeSource(BaseModel):
    endpoints : Optional[str] = Field(alias = "endpoints", default = None)
    path : Optional[str] = Field(alias = "path", default = None)
    read_only : Optional[bool] = Field(alias = "readOnly", default = None)
