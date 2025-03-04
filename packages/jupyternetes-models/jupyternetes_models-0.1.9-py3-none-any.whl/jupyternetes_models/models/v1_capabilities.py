from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional

class V1Capabilities(BaseModel):
    add : Optional[list[str]] = Field(alias = "add", default = None)
    drop : Optional[list[str]] = Field(alias = "drop", default = None)
