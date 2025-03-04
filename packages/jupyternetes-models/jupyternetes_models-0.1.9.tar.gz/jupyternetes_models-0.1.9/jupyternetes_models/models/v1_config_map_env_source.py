from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional

class V1ConfigMapEnvSource(BaseModel):
    name : Optional[str] = Field(alias = "name", default = None)
    optional : Optional[bool] = Field(alias = "optional", default = None)