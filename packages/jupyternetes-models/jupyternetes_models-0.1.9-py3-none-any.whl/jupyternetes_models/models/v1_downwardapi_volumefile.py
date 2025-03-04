from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_object_field_selector import V1ObjectFieldSelector
from .v1_resource_field_selector import V1ResourceFieldSelector


class V1DownwardAPIVolumeFile(BaseModel):
    field_ref : Optional[V1ObjectFieldSelector] = Field(alias = "fieldRef", default = None)
    mode : Optional[int] = Field(alias = "mode", default = None)
    path : str = Field(alias = "path", default = None)
    resource_field_ref : Optional[V1ResourceFieldSelector] = Field(alias = "resourceFieldRef", default = None)
    