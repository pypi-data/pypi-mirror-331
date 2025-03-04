from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1KeyToPath(BaseModel):
    key : str = Field(default = None, alias = "key")
    mode : Optional[str] = Field(default = None, alias = "mode")
    path : str = Field(default = None, alias = "path")