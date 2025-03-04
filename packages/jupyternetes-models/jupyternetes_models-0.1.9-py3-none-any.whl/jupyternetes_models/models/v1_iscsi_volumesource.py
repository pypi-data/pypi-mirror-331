from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_local_object_reference import V1LocalObjectReference


class V1ISCSIVolumeSource(BaseModel):
    chap_auth_discovery : Optional[bool] = Field(default = None, alias = "chapAuthDiscovery")
    chap_auth_session : Optional[bool] = Field(default = None, alias = "chapAuthSession")
    fs_type : Optional[str] = Field(default = None, alias = "fsType")
    initiator_name : Optional[str] = Field(default = None, alias = "initiatorName")
    iqn : Optional[str] = Field(default = None, alias = "iqn")
    iscsi_interface : Optional[str] = Field(default = None, alias = "iscsiInterface")
    lun : Optional[int] = Field(default = None, alias = "lun")
    portals : Optional[list[str]] = Field(default = None, alias = "portals")
    read_only : Optional[bool] = Field(default = None, alias = "readOnly")
    secret_ref : Optional[V1LocalObjectReference] = Field(default = None, alias = "secretRef")
    target_portal : Optional[str] = Field(default = None, alias = "targetPortal")