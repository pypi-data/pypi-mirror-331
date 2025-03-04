from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_downwardapi_volumefile import V1DownwardAPIVolumeFile


class V1DownwardAPIVolumeSource(BaseModel):
    default_mode : Optional[int] = Field(alias = "defaultMode", default = None)
    items : Optional[list[V1DownwardAPIVolumeFile]] = Field(alias = "items", default = None)