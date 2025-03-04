from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1ObjectFieldSelector(BaseModel):
    api_version : Optional[str] = Field(default = None, alias = "apiVersion")
    field_path : str = Field(default = None, alias = "fieldPath")