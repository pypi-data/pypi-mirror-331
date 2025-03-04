from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1GRPCAction(BaseModel):
    port : int = Field(alias = "port", default = None)
    service : Optional[str] = Field(alias = "service", default = None)
