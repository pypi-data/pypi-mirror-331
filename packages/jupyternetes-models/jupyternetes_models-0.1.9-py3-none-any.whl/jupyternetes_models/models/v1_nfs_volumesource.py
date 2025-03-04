from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1NFSVolumeSource(BaseModel):
    path : str = Field(default = None, alias = "path")
    read_only : Optional[bool] = Field(default = None, alias = "readOnly")
    server : str = Field(default = None, alias = "server")