from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional


class V1VolumeDevice(BaseModel):
    device_path : str = Field(alias="devicePath", default = None)
    name : str = Field(alias="name", default = None)
