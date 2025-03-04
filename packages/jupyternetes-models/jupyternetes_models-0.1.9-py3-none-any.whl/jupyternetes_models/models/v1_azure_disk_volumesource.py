from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional

class V1AzureDiskVolumeSource(BaseModel):
    caching_mode : Optional[str] = Field(alias = "cachingMode", default = None)
    disk_name : str = Field(alias = "diskName", default = None)
    disk_uri : str = Field(alias = "diskUri", default = None)
    fs_type : Optional[str] = Field(alias = "fsType", default = None)
    kind : Optional[int] = Field(alias = "kind", default = None)
    read_only : Optional[bool] = Field(alias = "readOnly", default = None)
    
