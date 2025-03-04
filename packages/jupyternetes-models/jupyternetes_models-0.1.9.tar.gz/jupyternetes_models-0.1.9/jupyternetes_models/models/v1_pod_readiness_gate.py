from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1PodReadinessGate(BaseModel):
    condition_type : str = Field(alias = "conditionType", default = None)
