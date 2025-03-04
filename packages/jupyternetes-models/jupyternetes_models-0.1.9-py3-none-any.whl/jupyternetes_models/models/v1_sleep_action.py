from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1SleepAction(BaseModel):
    seconds : int = Field(default = None, alias = "seconds")