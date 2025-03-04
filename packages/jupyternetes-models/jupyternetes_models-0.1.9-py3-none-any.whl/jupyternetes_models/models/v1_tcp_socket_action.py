from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1TCPSocketAction(BaseModel):
    host : Optional[str] = Field(default = None, alias = "host")
    port : str = Field(default = None, alias = "port")