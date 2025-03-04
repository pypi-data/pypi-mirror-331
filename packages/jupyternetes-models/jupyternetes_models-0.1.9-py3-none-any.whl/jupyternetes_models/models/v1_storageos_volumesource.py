from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_local_object_reference import V1LocalObjectReference


class V1StorageOSVolumeSource(BaseModel):
    fs_type : Optional[str] = Field(default = None, alias = "fsType")
    read_only : Optional[bool] = Field(default = None, alias = "readOnly")
    secret_ref : Optional[V1LocalObjectReference] = Field(default = None, alias = "secretRef")
    volume_name : Optional[str] = Field(default = None, alias = "volumeName")
    volume_namespace : Optional[str] = Field(default = None, alias = "volumeNamespace")
    