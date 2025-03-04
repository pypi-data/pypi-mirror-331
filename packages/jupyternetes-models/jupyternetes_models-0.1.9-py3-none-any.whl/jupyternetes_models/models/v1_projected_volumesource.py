from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_volume_projection import V1VolumeProjection


class V1ProjectedVolumeSource(BaseModel):
    default_mode : Optional[int] = Field(default = None, alias="defaultMode")
    sources : Optional[list[V1VolumeProjection]] = Field(default = None, alias="sources")