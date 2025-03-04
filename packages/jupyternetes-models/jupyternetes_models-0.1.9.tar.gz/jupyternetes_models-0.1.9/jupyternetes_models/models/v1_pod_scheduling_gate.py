from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1PodSchedulingGate(BaseModel):
    name : str = Field(default = None, alias = "name")