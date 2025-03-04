from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_node_selector_term import V1NodeSelectorTerm


class V1NodeSelector(BaseModel):
    node_selector_terms : list[V1NodeSelectorTerm] = Field(alias="nodeSelectorTerms", default = None)