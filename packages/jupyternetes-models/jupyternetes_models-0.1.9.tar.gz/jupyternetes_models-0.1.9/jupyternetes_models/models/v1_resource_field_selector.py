from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1ResourceFieldSelector(BaseModel):
    container_name : Optional[str] = Field(default = None, alias = "containerName")
    divisor : Optional[str] = Field(default = None, alias = "divisor")
    resource : str = Field(default = None, alias = "resource")