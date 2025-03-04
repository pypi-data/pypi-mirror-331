from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_label_selector import V1LabelSelector


class V1PodAffinityTerm(BaseModel):
    label_selector : Optional[V1LabelSelector] = Field(default = None, alias = "labelSelector")
    match_label_keys : Optional[list[str]] = Field(default = None, alias = "matchLabelKeys")
    mismatch_label_keys : Optional[list[str]] = Field(default = None, alias = "mismatchLabelKeys")
    namespace_selector : Optional[V1LabelSelector] = Field(default = None, alias = "namespaceSelector")
    namespaces : Optional[list[str]] = Field(default = None, alias = "namespaces")
    topology_key : str = Field(default = None, alias = "topologyKey")