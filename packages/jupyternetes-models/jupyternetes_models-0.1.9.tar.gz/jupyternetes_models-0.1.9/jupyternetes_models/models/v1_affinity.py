from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_node_affinity import V1NodeAffinity
from .v1_pod_affinity import V1PodAffinity
from .v1_pod_anti_affinity import V1PodAntiAffinity

class V1Affinity(BaseModel):
    node_affinity : Optional[V1NodeAffinity] = Field(alias="nodeAffinity", default = None)    
    pod_affinity: Optional[V1PodAffinity] = Field(alias="podAffinity", default = None)
    pod_anti_affinity : Optional[V1PodAntiAffinity] = Field(alias="podAntiAffinity", default = None)