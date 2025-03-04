from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_local_object_reference import V1LocalObjectReference


class V1FlexVolumeSource(BaseModel):
    driver : str = Field(alias = "driver", default = None)
    fs_type : Optional[str] = Field(alias = "fsType", default = None)
    options : Optional[dict[str,str]] = Field(alias = "options", default = None)
    read_only : Optional[bool] = Field(alias = "readOnly", default = None)
    secret_ref : Optional[V1LocalObjectReference] = Field(alias = "secretRef", default = None)