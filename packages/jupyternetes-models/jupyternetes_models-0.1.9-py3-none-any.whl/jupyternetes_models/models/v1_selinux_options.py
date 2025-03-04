from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1SELinuxOptions(BaseModel):
    level : Optional[str] = Field(default = None, alias = "level")
    role : Optional[str] = Field(default = None, alias = "role")
    type : Optional[str] = Field(default = None, alias = "type") 
    user : Optional[str] = Field(default = None, alias = "user")

