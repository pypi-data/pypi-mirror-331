from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1PortworxVolumeSource(BaseModel):
    fs_type : Optional[str] = Field(default = None, alias = "fsType")
    read_only : Optional[bool] = Field(default = None, alias = "readOnly")
    volume_id : str = Field(default = None, alias = "volumeID")