from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_local_object_reference import V1LocalObjectReference


class V1CSIVolumeSource(BaseModel):
    driver : str = Field(alias = "driver", default = None)
    fs_type : Optional[str] = Field(alias = "fsType", default = None)
    node_publish_secret_ref : Optional[V1LocalObjectReference] = Field(alias = "nodePublishSecretRef", default = None)
    read_only : Optional[bool] = Field(alias = "readOnly", default = None)
    volume_attributes : Optional[dict[str, str]] = Field(alias = "volumeAttributes", default = None)