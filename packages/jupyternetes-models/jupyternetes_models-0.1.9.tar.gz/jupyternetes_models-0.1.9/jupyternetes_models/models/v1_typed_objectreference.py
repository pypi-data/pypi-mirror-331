from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional

class V1TypedObjectReference(BaseModel):
    api_group : Optional[str] = Field(default = None, alias = "apiGroup")
    kind : str = Field(alias = "kind", default = None)
    name : str = Field(alias = "name", default = None)
    namespace : Optional[str] = Field(default = None, alias = "namespace")