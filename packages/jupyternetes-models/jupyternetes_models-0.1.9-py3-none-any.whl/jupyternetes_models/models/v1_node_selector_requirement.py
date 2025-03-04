from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1NodeSelectorRequirement(BaseModel):
    key : str = Field(default = None, alias = "key")
    operator : str = Field(default = None, alias = "operator")
    values : Optional[list[str]] = Field(default = None, alias = "values")