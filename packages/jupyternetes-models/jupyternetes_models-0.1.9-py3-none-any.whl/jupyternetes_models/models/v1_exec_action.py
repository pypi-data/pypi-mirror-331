from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1ExecAction(BaseModel):
    command : list[str] = Field(alias = "command", default = None)
