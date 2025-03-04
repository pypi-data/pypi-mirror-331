from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1FlockerVolumeSource(BaseModel):
    dataset_name : Optional[str] = Field(alias = "datasetName", default = None)
    dataset_uuid : Optional[str] = Field(alias = "datasetUUID", default = None)