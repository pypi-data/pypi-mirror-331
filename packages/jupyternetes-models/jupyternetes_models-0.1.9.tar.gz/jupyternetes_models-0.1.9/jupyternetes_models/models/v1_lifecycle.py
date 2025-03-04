from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_lifecycle_handler import V1LifecycleHandler


class V1Lifecycle(BaseModel):
    post_start : Optional[V1LifecycleHandler] = Field(alias="postStart", default = None)
    pre_stop : Optional[V1LifecycleHandler] = Field(alias="preStop", default = None)