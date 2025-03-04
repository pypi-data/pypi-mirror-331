from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_local_object_reference import V1LocalObjectReference

class V1CephFSVolumeSource(BaseModel):
    monitors : list[str] = Field(alias = "monitors", default = None)
    path : Optional[str] = Field(alias = "path", default = None)
    read_only : Optional[bool] = Field(alias = "readOnly", default = None)
    secret_file : Optional[str] = Field(alias = "secretFile", default = None)
    secret_ref : Optional[V1LocalObjectReference] = Field(alias = "secretRef", default = None)
    user : Optional[str] = Field(alias = "user", default = None)