from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_local_object_reference import V1LocalObjectReference


class V1ScaleIOVolumeSource(BaseModel):
    fs_type : Optional[str] = Field(default = None, alias = "fsType")
    gateway : str = Field(default = None, alias = "gateway")
    protection_domain : Optional[str] = Field(default = None, alias = "protectionDomain")
    read_only : Optional[bool] = Field(default = None, alias = "readOnly")
    secret_ref : Optional[V1LocalObjectReference] = Field(default = None, alias = "secretRef")
    ssl_enabled : Optional[bool] = Field(default = None, alias = "sslEnabled")
    storage_mode : Optional[str] = Field(default = None, alias = "storageMode")
    storage_pool : Optional[str] = Field(default = None, alias = "storagePool")
    system : str = Field(default = None, alias = "system")
    volume_name : Optional[str] = Field(default = None, alias = "volumeName")
    