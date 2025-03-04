from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_http_header import V1HTTPHeader


class V1HTTPGetAction(BaseModel):
    host : Optional[str] = Field(default = None, alias = "host")
    http_headers : Optional[list[V1HTTPHeader]] = Field(default = None, alias = "httpHeaders")
    path : Optional[str] = Field(default = None, alias = "path")
    scheme : Optional[str] = Field(default = None, alias = "scheme")
    port : str = Field(default = None, alias = "port")
