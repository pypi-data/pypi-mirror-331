from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_config_map_env_source import V1ConfigMapEnvSource
from .v1_secret_env_source import V1SecretEnvSource


class V1EnvFromSource(BaseModel):
    config_map_ref : Optional[V1ConfigMapEnvSource] = Field(alias = "configMapRef", default = None)
    prefix : Optional[str] = Field(alias = "prefix", default = None)
    secret_ref : Optional[V1SecretEnvSource] = Field(alias = "secretRef", default = None)