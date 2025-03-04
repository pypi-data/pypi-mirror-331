from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional

class V1ContainerPort(BaseModel):
    container_port : int = Field(alias = "containerPort", default = None)
    host_ip : Optional[str] = Field(alias = "hostIp", default = None)
    host_port : Optional[int] = Field(alias = "hostPort", default = None)
    name : Optional[str] = Field(alias = "name", default = None)
    protocol : Optional[str] = Field(alias = "protocol", default = None)