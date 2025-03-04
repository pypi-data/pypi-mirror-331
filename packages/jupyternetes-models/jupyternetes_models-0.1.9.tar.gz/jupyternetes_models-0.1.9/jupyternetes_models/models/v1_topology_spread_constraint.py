from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_label_selector import V1LabelSelector


class V1TopologySpreadConstraint(BaseModel):
    label_selector : Optional[V1LabelSelector] = Field(default = None, alias = "labelSelector")
    match_label_keys : Optional[list[str]] = Field(default = None, alias = "matchLabelKeys")
    max_skew : Optional[int] = Field(default = None, alias = "maxSkew")
    min_domains : Optional[int] = Field(default = None, alias = "minDomains")
    node_affinity_policy : Optional[str] = Field(default = None, alias = "nodeAffinityPolicy")
    node_taints_policy : Optional[str] = Field(default = None, alias = "nodeTaintsPolicy")
    topology_key : str = Field(alias = "topologyKey", default = None)
    when_unsatisfiable : Optional[str] = Field(default = None, alias = "whenUnsatisfiable")