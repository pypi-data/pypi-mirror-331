from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_local_object_reference import V1LocalObjectReference


class V1RBDVolumeSource(BaseModel):
    fs_type : Optional[str] = Field(default = None, alias = "fsType")
    image : str = Field(default = None, alias = "image")
    keyring : Optional[str] = Field(default = None, alias = "keyring")
    monitors : Optional[list[str]] = Field(default = None, alias = "monitors")
    pool : Optional[str] = Field(default = None, alias = "pool")
    read_only : Optional[bool] = Field(default = None, alias = "readOnly")
    secret_ref : Optional[V1LocalObjectReference] = Field(default = None, alias = "secretRef")
    user : Optional[str] = Field(default = None, alias = "user")
    