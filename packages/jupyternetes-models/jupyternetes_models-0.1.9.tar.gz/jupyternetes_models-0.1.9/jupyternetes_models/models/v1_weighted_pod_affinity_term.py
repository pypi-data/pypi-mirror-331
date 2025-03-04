from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_pod_affinity_term import V1PodAffinityTerm


class V1WeightedPodAffinityTerm(BaseModel):
    pod_affinity_term : V1PodAffinityTerm = Field(alias="podAffinityTerm", default = None)
    weight : int = Field(default = None, alias = "weight")