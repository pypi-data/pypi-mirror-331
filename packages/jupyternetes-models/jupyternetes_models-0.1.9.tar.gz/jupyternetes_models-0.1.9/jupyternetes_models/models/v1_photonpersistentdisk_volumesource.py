from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1PhotonPersistentDiskVolumeSource(BaseModel):
    fs_type : Optional[str] = Field(default = None, alias = "fsType")
    pd_id : str = Field(default = None, alias = "pdID")