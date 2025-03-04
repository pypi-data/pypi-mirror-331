from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_node_selector_term import V1NodeSelectorTerm


class V1PreferredSchedulingTerm(BaseModel):
    preference : V1NodeSelectorTerm = Field(alias="preference", default = None)
    weight : int = Field(alias="weight", default = None)