from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1PersistentVolumeClaimVolumeSource(BaseModel):
    claim_name : str = Field(default = None, alias = "claimName")
    read_only : Optional[bool] = Field(default = None, alias = "readOnly")