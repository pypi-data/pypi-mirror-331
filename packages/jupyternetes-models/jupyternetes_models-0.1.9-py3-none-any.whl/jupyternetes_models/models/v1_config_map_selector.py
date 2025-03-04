from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional

class V1ConfigMapKeySelector(BaseModel):
    key : str = Field(alias = "key", default = None)
    name : Optional[str] = Field(alias = "name", default = None)
    optional : Optional[bool] = Field(alias = "optional", default = None)