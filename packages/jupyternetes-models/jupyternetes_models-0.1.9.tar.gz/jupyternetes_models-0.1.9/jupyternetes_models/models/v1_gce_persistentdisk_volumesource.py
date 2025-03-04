from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1GCEPersistentDiskVolumeSource(BaseModel):
    fs_type : Optional[str] = Field(alias = "fsType", default = None)
    partition : Optional[int] = Field(alias = "partition", default = None)
    pd_name : str = Field(alias = "pdName", default = None)
    read_only : Optional[bool] = Field(alias = "readOnly", default = None)
