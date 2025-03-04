from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_persistentvolumeclaim_template import V1PersistentVolumeClaimTemplate


class V1EphemeralVolumeSource(BaseModel):
    volume_claim_template : Optional[V1PersistentVolumeClaimTemplate] = Field(alias = "volumeClaimTemplate", default = None)
