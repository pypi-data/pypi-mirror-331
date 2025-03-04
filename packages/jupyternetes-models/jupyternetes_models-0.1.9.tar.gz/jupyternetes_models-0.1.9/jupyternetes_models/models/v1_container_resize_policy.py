from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional

class V1ContainerResizePolicy(BaseModel):
    resource_name : str = Field(alias = "resourceName", default = None)
    restart_policy : str = Field(alias = "restartPolicy", default = None)