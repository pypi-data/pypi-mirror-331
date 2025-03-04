from pydantic import BaseModel, Field, SkipValidation, ConfigDict
from typing import Optional
from .v1_label_selector_requirement import V1LabelSelectorRequirement


class V1LabelSelector(BaseModel):
    match_expressions : Optional[V1LabelSelectorRequirement] = Field(default = None, alias = "matchExpressions")
    match_labels : Optional[dict[str,str]] = Field(default = None, alias = "matchLabels")