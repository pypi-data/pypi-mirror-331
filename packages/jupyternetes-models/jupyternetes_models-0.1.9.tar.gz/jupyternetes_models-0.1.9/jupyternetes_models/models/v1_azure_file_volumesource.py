from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional

class V1AzureFileVolumeSource(BaseModel):
    read_only : Optional[bool] = Field(alias = "readOnly", default = None)
    secret_name : str = Field(alias = "secretName", default = None)
    share_name : str = Field(alias = "shareName", default = None)
