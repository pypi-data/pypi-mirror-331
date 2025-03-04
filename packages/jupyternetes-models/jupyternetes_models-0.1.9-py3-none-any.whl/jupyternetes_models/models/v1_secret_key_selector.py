from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1SecretKeySelector(BaseModel):
    key : str = Field(default = None, alias = "key")
    name : Optional[str] = Field(default = None, alias = "name")
    optional : Optional[bool] = Field(default = None, alias = "optional")