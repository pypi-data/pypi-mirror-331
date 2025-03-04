from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1QuobyteVolumeSource(BaseModel):
    group : Optional[str] = Field(default = None, alias = "group")
    read_only : Optional[bool] = Field(default = None, alias = "readOnly")
    registry : str = Field(alias = "registry", default = None)
    tenant : Optional[str] = Field(default = None, alias = "tenant")
    user : Optional[str] = Field(default = None, alias = "user")
    volume : str = Field(default = None, alias = "volume")