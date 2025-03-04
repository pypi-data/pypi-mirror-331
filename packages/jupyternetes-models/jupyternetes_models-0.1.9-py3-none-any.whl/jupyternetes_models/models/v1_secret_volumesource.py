from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_keytopath import V1KeyToPath


class V1SecretVolumeSource(BaseModel):
    default_mode : Optional[int] = Field(default = None, alias = "defaultMode")
    items : Optional[list[V1KeyToPath]] = Field(default = None, alias = "items")
    optional : Optional[bool] = Field(default = None, alias = "optional")
    secret_name : Optional[str] = Field(default = None, alias = "secretName")
