from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_env_var_source import V1EnvVarSource


class V1EnvVar(BaseModel):
    name : str = Field(alias = "name", default = None)
    value : Optional[str] = Field(alias = "value", default = None)
    value_from : Optional[V1EnvVarSource] = Field(alias = "valueFrom", default = None)