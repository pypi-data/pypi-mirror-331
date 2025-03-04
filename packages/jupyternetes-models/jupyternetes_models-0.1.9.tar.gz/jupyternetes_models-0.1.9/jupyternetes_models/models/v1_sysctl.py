from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1Sysctl(BaseModel):
    name : str = Field(alias = "name", default = None)
    value : str = Field(alias = "value", default = None)