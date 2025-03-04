from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_config_map_selector import V1ConfigMapKeySelector
from .v1_object_field_selector import V1ObjectFieldSelector
from .v1_resource_field_selector import V1ResourceFieldSelector
from .v1_secret_key_selector import V1SecretKeySelector


class V1EnvVarSource(BaseModel):
    config_map_key_ref : Optional[V1ConfigMapKeySelector] = Field(alias = "configMapKeyRef", default = None)
    field_ref : Optional[V1ObjectFieldSelector] = Field(alias = "fieldRef", default = None)
    resource_field_ref : Optional[V1ResourceFieldSelector] = Field(alias = "resourceFieldRef", default = None)
    secret_key_ref : Optional[V1SecretKeySelector] = Field(alias = "secretKeyRef", default = None)