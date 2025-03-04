from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_local_object_reference import V1LocalObjectReference

class V1CinderVolumeSource(BaseModel):
    fs_type : Optional[str] = Field(alias = "fsType", default = None)
    read_only : Optional[bool] = Field(alias = "readOnly", default = None)
    secret_ref : Optional[V1LocalObjectReference] = Field(alias = "secretRef", default = None)
    volume_id : str = Field(alias = "volumeID", default = None)