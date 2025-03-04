from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1FCVolumeSource(BaseModel):
    fs_type : Optional[str] = Field(alias = "fsType", default = None)
    lun : Optional[int] = Field(alias = "lun", default = None)
    read_only : Optional[bool] = Field(alias = "readOnly", default = None)
    target_ww_ns : Optional[list[str]] = Field(alias = "targetWWNS", default = None)
    wwids : Optional[list[str]] = Field(alias = "wwids", default = None)
