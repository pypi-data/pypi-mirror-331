from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional

from .v1_preferred_scheduling_term import V1PreferredSchedulingTerm
from .v1_node_selector import V1NodeSelector


class V1NodeAffinity(BaseModel):
    preferred_during_scheduling_ignored_during_execution : Optional[list[V1PreferredSchedulingTerm]] = Field(default = None, alias = "preferredDuringSchedulingIgnoredDuringExecution")
    required_during_scheduling_ignored_during_execution : Optional[V1NodeSelector] = Field(default = None, alias = "requiredDuringSchedulingIgnoredDuringExecution")