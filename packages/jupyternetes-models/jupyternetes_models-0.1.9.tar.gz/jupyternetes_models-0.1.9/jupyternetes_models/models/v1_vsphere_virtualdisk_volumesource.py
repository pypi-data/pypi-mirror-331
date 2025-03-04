from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1VsphereVirtualDiskVolumeSource(BaseModel):
    fs_type : Optional[str] = Field(default = None, alias = "fsType")
    storage_policy_id : Optional[str] = Field(default = None, alias = "storagePolicyID")
    storage_policy_name : Optional[str] = Field(default = None, alias = "storagePolicyName")
    volume_path : str = Field(alias = "volumePath", default = None)