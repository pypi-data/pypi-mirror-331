from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1SeccompProfile(BaseModel):
    localhost_profile : Optional[str] = Field(default = None, alias = "localhostProfile")
    type : str = Field(default = None, alias = "type")
