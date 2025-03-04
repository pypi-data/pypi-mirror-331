from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional

from .v1_weighted_pod_affinity_term import V1WeightedPodAffinityTerm
from .v1_pod_affinity_term import V1PodAffinityTerm


class V1PodAffinity(BaseModel):
    preferred_during_scheduling_ignored_during_execution : Optional[list[V1WeightedPodAffinityTerm]] = Field(default = None, alias = "preferredDuringSchedulingIgnoredDuringExecution")
    required_during_scheduling_ignored_during_execution : Optional[list[V1PodAffinityTerm]] = Field(default = None, alias = "requiredDuringSchedulingIgnoredDuringExecution")
    