from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_node_selector_requirement import V1NodeSelectorRequirement


class V1NodeSelectorTerm(BaseModel):
    match_expressions : Optional[list[V1NodeSelectorRequirement]] = Field(default = None, alias = "matchExpressions")
    match_fields : Optional[list[V1NodeSelectorRequirement]] = Field(default = None, alias = "matchFields")