from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_downwardapi_volumefile import V1DownwardAPIVolumeFile


class V1DownwardAPIProjection(BaseModel):
    items : Optional[list[V1DownwardAPIVolumeFile]] = Field(alias = "items", default = None)