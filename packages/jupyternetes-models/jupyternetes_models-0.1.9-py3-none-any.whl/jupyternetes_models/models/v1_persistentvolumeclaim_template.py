from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_objectmeta import V1ObjectMeta
from .v1_persistentvolumeclaim_spec import V1PersistentVolumeClaimSpec


class V1PersistentVolumeClaimTemplate(BaseModel):
    metadata : Optional[V1ObjectMeta] = Field(default = None, alias = "metadata")
    spec : V1PersistentVolumeClaimSpec = Field(default = None, alias = "spec")