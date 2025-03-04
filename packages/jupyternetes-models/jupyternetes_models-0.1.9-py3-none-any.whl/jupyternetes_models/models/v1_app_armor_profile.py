from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional

class V1AppArmorProfile(BaseModel):
    localhost_profile : Optional[str] = Field(alias="localhostProfile", default = None)
    type : str = Field(alias="type", default = None)