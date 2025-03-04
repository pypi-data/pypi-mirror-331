from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1SecretEnvSource(BaseModel):
    name : Optional[str] = Field(default = None, alias = "name")
    optional : Optional[bool] = Field(default = None, alias = "optional")